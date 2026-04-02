# pdf_report_service
Микросервис для формирования pdf файла репорта

Имеет только одну ручку: `/report-pdf/`

Пример запроса:

    curl --location 'http://0.0.0.0:7772/report-pdf/?report_id=1&token=test_token&source=dev&subdomain=dev' \
    --data ''
