from pathlib import Path


def test_nginx_example_redirects_http_to_https():
    config = Path("deployment/nginx.conf.example").read_text(encoding="utf-8")
    http_server = config.split("server {", 2)[1]

    assert "return 301 https://$host$request_uri;" in http_server
    assert "proxy_pass http://127.0.0.1:8010;" not in http_server
