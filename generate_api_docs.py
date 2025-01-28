from fastapi.openapi.utils import get_openapi
import json
from pathlib import Path

from main import app


def generate_markdown_docs():
    """Generate Markdown documentation from OpenAPI schema"""
    # OpenAPI 스키마 가져오기
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 마크다운 문서 시작
    md_content = f"""# {openapi_schema['info']['title']} API 문서
Version: {openapi_schema['info']['version']}

{openapi_schema['info']['description']}

## API Endpoints
"""

    # 태그별로 정리
    endpoints_by_tag = {}
    for path, path_item in openapi_schema['paths'].items():
        for method, operation in path_item.items():
            if 'tags' in operation and operation['tags']:
                tag = operation['tags'][0]
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append({
                    'path': path,
                    'method': method.upper(),
                    'summary': operation.get('summary', ''),
                    'description': operation.get('description', ''),
                    'parameters': operation.get('parameters', []),
                    'requestBody': operation.get('requestBody', None),
                    'responses': operation.get('responses', {})
                })

    # 마크다운으로 변환
    for tag, endpoints in endpoints_by_tag.items():
        md_content += f"### {tag}\n\n"
        for endpoint in endpoints:
            md_content += f"#### {endpoint['method']} {endpoint['path']}\n"
            if endpoint['summary']:
                md_content += f"{endpoint['summary']}\n\n"
            if endpoint['description']:
                md_content += f"{endpoint['description']}\n\n"

            if endpoint['parameters']:
                md_content += "**Parameters:**\n\n"
                for param in endpoint['parameters']:
                    md_content += f"- {param['name']} ({param['in']}): {param.get('description', '')}\n"
                md_content += "\n"

            if endpoint['requestBody']:
                md_content += "**Request Body:**\n\n"
                if 'content' in endpoint['requestBody']:
                    for content_type, content in endpoint['requestBody']['content'].items():
                        md_content += f"Content-Type: {content_type}\n\n"
                        if 'schema' in content:
                            md_content += "Schema:\n```json\n"
                            md_content += json.dumps(content['schema'], indent=2)
                            md_content += "\n```\n\n"

            md_content += "**Responses:**\n\n"
            for status_code, response in endpoint['responses'].items():
                md_content += f"- {status_code}: {response.get('description', '')}\n"
            md_content += "\n---\n\n"

    # docs 디렉토리 생성
    Path("docs").mkdir(exist_ok=True)

    # 마크다운 파일 저장
    with open("docs/api.md", "w") as f:
        f.write(md_content)


if __name__ == "__main__":
    generate_markdown_docs()