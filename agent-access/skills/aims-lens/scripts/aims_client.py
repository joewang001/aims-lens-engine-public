#!/usr/bin/env python3
"""AIMS contract-preview client. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

SPEC = json.loads((Path(__file__).resolve().parents[1] / 'references' / 'openapi.json').read_text(encoding='utf-8'))
OPERATIONS = {op['operationId']: (method.upper(), path, op)
              for path, verbs in SPEC['paths'].items() for method, op in verbs.items()}
MAX_UPLOAD = 8 * 1024 * 1024
MAX_RESPONSE = 10 * 1024 * 1024
RESERVED = {'organization_id', 'tenant_id', 'actor_id', 'user_id', 'principal_id', 'key_id',
            'builder_version', 'policy_version', 'candidate', 'candidate_profile', 'candidate_resume',
            'candidate_pii', 'candidate_answer', 'candidate_score', 'candidate_result',
            'candidate_transcript', 'candidate_assessment', 'resume', 'transcript'}


class ClientError(Exception):
    def __init__(self, code, message, exit_code=2, **safe):
        self.code, self.message, self.exit_code, self.safe = code, message, exit_code, safe


def check_schema(value, schema, path='$'):
    """Validate the bounded JSON Schema vocabulary used by this bundled contract."""
    if '$ref' in schema:
        schema = SPEC['components']['schemas'][schema['$ref'].rsplit('/', 1)[1]]
    if 'oneOf' in schema:
        matches = 0
        for option in schema['oneOf']:
            try:
                check_schema(value, option, path)
                matches += 1
            except ClientError:
                pass
        if matches != 1:
            raise ClientError('SCHEMA_INVALID', 'Value does not match exactly one permitted schema.')
        return
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])):
        raise ClientError('SCHEMA_INVALID', 'A fixed contract value does not match.')
    if 'enum' in schema and value not in schema['enum']:
        raise ClientError('SCHEMA_INVALID', 'Value is outside the permitted enum.')
    kind = schema.get('type')
    kinds = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    if kind and type(value) is not kinds[kind]:
        raise ClientError('SCHEMA_INVALID', 'JSON value has the wrong type.')
    if kind == 'object':
        props = schema.get('properties', {})
        if set(schema.get('required', [])) - value.keys():
            raise ClientError('SCHEMA_INVALID', 'A required field is missing.')
        if schema.get('additionalProperties') is False and value.keys() - props.keys():
            raise ClientError('SCHEMA_INVALID', 'An unsupported field was supplied.')
        for key, child in value.items():
            if key in props:
                check_schema(child, props[key], path + '.' + key)
    if kind == 'string':
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            raise ClientError('SCHEMA_INVALID', 'String length is outside the contract limit.')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ClientError('SCHEMA_INVALID', 'String format is invalid.')
    if kind == 'integer' and not schema.get('minimum', -float('inf')) <= value <= schema.get('maximum', float('inf')):
        raise ClientError('SCHEMA_INVALID', 'Number is outside the contract limit.')
    if kind == 'array':
        if not schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', float('inf')):
            raise ClientError('SCHEMA_INVALID', 'Array length is outside the contract limit.')
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ClientError('SCHEMA_INVALID', 'Array contains duplicates.')
        for child in value:
            check_schema(child, schema['items'], path + '[]')


def reject_reserved(value):
    if isinstance(value, dict):
        if RESERVED & {str(k).lower() for k in value}:
            raise ClientError('PROHIBITED_INPUT', 'Tenant, actor, builder and candidate fields cannot be supplied.')
        for child in value.values():
            reject_reserved(child)
    elif isinstance(value, list):
        for child in value:
            reject_reserved(child)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def origin_url(raw, allow_mock):
    p = urllib.parse.urlsplit(raw)
    if p.username or p.password or p.query or p.fragment or p.path not in ('', '/'):
        raise ClientError('INVALID_ORIGIN', 'Base URL must be an allowed origin without credentials, path, query or fragment.')
    if raw.rstrip('/') == 'https://portal.aimslens.com':
        return raw.rstrip('/')
    if allow_mock and p.scheme == 'http' and p.hostname in ('127.0.0.1', '::1') and p.port:
        return raw.rstrip('/')
    raise ClientError('INVALID_ORIGIN', 'Use the fixed AIMS HTTPS origin or an explicitly enabled loopback mock origin.')


def parse_json(data):
    def pairs(items):
        result = {}
        for key, val in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = val
        return result
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))


def prepare(args):
    method, path, op = OPERATIONS[args.operation]
    ids = {'role_id': args.role, 'submission_id': args.submission, 'lens_id': args.lens, 'lens_version': args.version}
    for name, value in ids.items():
        if '{' + name + '}' in path:
            if name == 'lens_version':
                if value is None or value < 1:
                    raise ClientError('INVALID_RESOURCE', 'A positive Lens version is required.')
            elif not value or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
                raise ClientError('INVALID_RESOURCE', 'A valid resource ID is required.')
            path = path.replace('{' + name + '}', str(value))
        elif value is not None:
            raise ClientError('INVALID_ARGUMENT', 'A resource argument does not apply to this operation.')
    headers = {'Accept': 'application/json'}
    if method == 'POST':
        if not args.key or not re.fullmatch(r'[A-Za-z0-9._:-]{8,128}', args.key):
            raise ClientError('IDEMPOTENCY_KEY_REQUIRED', 'Persist and supply an 8-128 character idempotency key.')
        headers['Idempotency-Key'] = args.key
    elif args.key:
        raise ClientError('INVALID_ARGUMENT', 'Read operations do not accept an idempotency key.')
    payload = None
    body = None
    if args.operation == 'material-file':
        if args.body or not args.file or not args.document_type:
            raise ClientError('INVALID_FILE_INPUT', 'File upload requires --file and --document-type, without --body.')
        file = Path(args.file)
        mime = {'.pdf': 'application/pdf', '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.txt': 'text/plain'}.get(file.suffix.lower())
        if not mime or not file.is_file() or not 0 < file.stat().st_size <= MAX_UPLOAD:
            raise ClientError('INVALID_FILE_INPUT', 'Supply a nonempty PDF, DOCX or TXT file of at most 8 MiB.')
        with file.open('rb') as stream:
            data = stream.read(MAX_UPLOAD + 1)
        if len(data) > MAX_UPLOAD:
            raise ClientError('INVALID_FILE_INPUT', 'File grew beyond the upload limit.')
        payload = {'document_type': args.document_type, 'title': args.title or '',
                   'file_sha256': hashlib.sha256(data).hexdigest(), 'file': 'binary-upload:' + str(len(data))}
        check_schema(payload, op['requestBody']['content']['multipart/form-data']['schema'])
        boundary = 'aims_' + uuid.uuid4().hex
        parts = []
        for key, value in payload.items():
            if key != 'file':
                parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode('utf-8'))
        # A neutral filename prevents local path/header injection; content is unchanged.
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="upload{file.suffix.lower()}"\r\nContent-Type: {mime}\r\n\r\n'.encode('ascii'))
        parts.extend([data, f'\r\n--{boundary}--\r\n'.encode('ascii')])
        body = b''.join(parts)
        headers['Content-Type'] = 'multipart/form-data; boundary=' + boundary
    elif 'requestBody' in op:
        if not args.body:
            raise ClientError('BODY_REQUIRED', 'Supply an authorized JSON payload file with --body.')
        with Path(args.body).open('rb') as stream:
            raw = stream.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ClientError('INVALID_INPUT', 'JSON input exceeds the preview limit.')
        payload = parse_json(raw)
        reject_reserved(payload)
        check_schema(payload, op['requestBody']['content']['application/json']['schema'])
        body = canonical(payload)
        headers['Content-Type'] = 'application/json'
    elif args.body:
        raise ClientError('INVALID_ARGUMENT', 'This operation does not accept a request body.')
    if args.operation != 'material-file' and any(x is not None for x in (args.file, args.document_type, args.title)):
        raise ClientError('INVALID_ARGUMENT', 'File arguments apply only to material-file.')
    return method, path, op, headers, body, payload


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def wire(origin, path, method, headers, body, token, timeout):
    request = urllib.request.Request(origin + '/agent/v1' + path, data=body, method=method,
                                    headers={**headers, 'Authorization': 'Bearer ' + token})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        response = exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ClientError('TRANSPORT_UNKNOWN', 'Request outcome is unknown; preserve the original key before reconciling.',
                          4, retryable=True) from exc
    try:
        with response:
            status = response.code
            raw = response.read(MAX_RESPONSE + 1)
            media = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
            retry_after = response.headers.get('Retry-After', '')
    except (TimeoutError, OSError, http.client.HTTPException) as exc:
        raise ClientError('TRANSPORT_UNKNOWN', 'Response was interrupted; preserve the original key.', 4, retryable=True) from exc
    if token in raw.decode('utf-8', errors='replace'):
        raise ClientError('CREDENTIAL_REFLECTION', 'Response was withheld because it reflected a credential.')
    if 300 <= status < 400:
        raise ClientError('REDIRECT_BLOCKED', 'Redirect rejected; no credential was forwarded.', 3, http_status=status)
    if len(raw) > MAX_RESPONSE or media != 'application/json':
        raise ClientError('INVALID_RESPONSE', 'Response must be bounded JSON; operation outcome may be unknown.',
                          3, http_status=status)
    try:
        result = parse_json(raw)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ClientError('INVALID_RESPONSE', 'Response is not valid JSON; operation outcome may be unknown.', 3,
                          http_status=status) from exc
    if not 200 <= status < 300:
        try:
            check_schema(result, SPEC['components']['schemas']['Error'])
        except ClientError as exc:
            raise ClientError('INVALID_RESPONSE', 'API error did not match the contract.', 3, http_status=status) from exc
        safe_id = result['request_id'] if re.fullmatch(r'[A-Za-z0-9_-]{1,128}', result['request_id']) else None
        safe = dict(http_status=status, request_id=safe_id, retryable=result['error']['retryable'])
        if retry_after.isdigit() and len(retry_after) <= 8:
            safe['retry_after_seconds'] = int(retry_after)
        raise ClientError(result['error']['code'], 'API request rejected; inspect request ID using authorized support tools.', 3, **safe)
    return status, result


def validated_wire(origin, path, method, op, headers, body, token, timeout):
    status, result = wire(origin, path, method, headers, body, token, timeout)
    response = op['responses'].get(str(status))
    if response is None:
        raise ClientError('INVALID_RESPONSE', 'Unexpected success HTTP status.')
    try:
        check_schema(result, response['content']['application/json']['schema'])
    except ClientError as exc:
        raise ClientError('INVALID_RESPONSE', 'Success response did not match the bundled contract.') from exc
    return result


def run(args):
    origin = origin_url(args.base_url, args.allow_local_mock)
    method, path, op, headers, body, payload = prepare(args)
    if not args.execute:
        return {'mode': 'dry_run', 'operation': args.operation, 'method': method,
                'url': origin + '/agent/v1' + path, 'credential_loaded': False,
                'idempotency_key': args.key, 'body_bytes': len(body or b''),
                'payload_sha256': hashlib.sha256(canonical(payload)).hexdigest() if payload else None}
    token = os.environ.get('AIMS_API_KEY', '')
    if not re.fullmatch(r'[A-Za-z0-9._~+/-]{16,4096}={0,2}', token):
        raise ClientError('CREDENTIAL_REQUIRED', 'Harness must inject a valid AIMS_API_KEY through its secret store.')
    if not 0 < args.timeout <= 120:
        raise ClientError('INVALID_TIMEOUT', 'Timeout must be between 0 and 120 seconds.')
    if args.operation != 'capabilities':
        _, cap_path, cap_op = OPERATIONS['capabilities']
        cap = validated_wire(origin, cap_path, 'GET', cap_op, {'Accept': 'application/json'}, None, token, args.timeout)['data']
        if args.operation not in cap['operations']:
            raise ClientError('CAPABILITY_UNAVAILABLE', 'Operation is disabled for this principal.')
        if args.operation == 'material-file' and int(payload['file'].split(':')[1]) > cap['max_upload_bytes']:
            raise ClientError('INVALID_FILE_INPUT', 'File exceeds the server upload limit.')
    result = validated_wire(origin, path, method, op, headers, body, token, args.timeout)
    if args.operation == 'role-get' and result['data']['role_id'] != args.role:
        raise ClientError('SOURCE_MISMATCH', 'Returned role does not match the requested ID.')
    if args.operation in ('material-text', 'material-url', 'material-file'):
        data = result['data']
        expected_kind = args.operation.rsplit('-', 1)[1].upper()
        if data['document_type'] != payload['document_type'] or data['source_kind'] != expected_kind:
            raise ClientError('SOURCE_MISMATCH', 'Returned material does not match its requested type.')
        expected_hash = payload.get('file_sha256')
        if args.operation == 'material-text':
            expected_hash = hashlib.sha256(payload['text'].encode('utf-8')).hexdigest()
        if expected_hash and data['sha256'] != expected_hash:
            raise ClientError('MATERIAL_DIGEST_MISMATCH', 'Stored material digest does not match the supplied bytes.')
    if args.operation in ('submission-freeze', 'submission-get'):
        data = result['data']
        if args.operation == 'submission-get' and data['submission_id'] != args.submission:
            raise ClientError('SOURCE_MISMATCH', 'Returned Submission does not match the requested ID.')
        if args.operation == 'submission-freeze' and (data['role_id'] != args.role or data['source_revision'] != payload['expected_source_revision']):
            raise ClientError('SOURCE_MISMATCH', 'Frozen source does not match the requested role and revision.')
    if args.operation in ('lens-build', 'lens-get'):
        data = result['data']
        meta = data['lens']['meta']
        if data['lens']['scope']['submission_ref'] != meta['submission_ref']:
            raise ClientError('SOURCE_MISMATCH', 'Lens scope and metadata refer to different Submissions.')
        if args.operation == 'lens-build' and (meta['submission_ref'] != args.submission or meta['source_snapshot_sha256'] != payload['expected_snapshot_sha256']):
            raise ClientError('SOURCE_MISMATCH', 'Lens source does not match the requested frozen Submission.')
        if args.operation == 'lens-get' and (meta['lens_id'] != args.lens or meta['lens_version'] != args.version):
            raise ClientError('SOURCE_MISMATCH', 'Lens does not match the exact requested version.')
        if hashlib.sha256(canonical(data['lens'])).hexdigest() != data['lens_sha256']:
            raise ClientError('LENS_DIGEST_MISMATCH', 'Lens digest does not match the received object.')
        if data.get('mock_only') and not args.allow_local_mock:
            raise ClientError('MOCK_RESPONSE_BLOCKED', 'Mock artifact is not a production Lens.')
    return {'mode': 'execute', 'operation': args.operation, **result}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=sorted(OPERATIONS))
    p.add_argument('--base-url', default='https://portal.aimslens.com')
    p.add_argument('--allow-local-mock', action='store_true')
    p.add_argument('--execute', action='store_true')
    p.add_argument('--body')
    p.add_argument('--role')
    p.add_argument('--submission')
    p.add_argument('--lens')
    p.add_argument('--version', type=int)
    p.add_argument('--key')
    p.add_argument('--file')
    p.add_argument('--document-type')
    p.add_argument('--title')
    p.add_argument('--timeout', type=float, default=30)
    return p


def main(argv=None):
    try:
        result = run(parser().parse_args(argv))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0
    except ClientError as exc:
        print(json.dumps({'status': 'error', 'error': {'code': exc.code, 'message': exc.message, **exc.safe}}))
        return exc.exit_code
    except (OSError, ValueError, UnicodeError, RecursionError):
        print(json.dumps({'status': 'error', 'error': {'code': 'INVALID_LOCAL_INPUT',
                          'message': 'Input file, JSON or configuration is invalid; sensitive details were withheld.'}}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
