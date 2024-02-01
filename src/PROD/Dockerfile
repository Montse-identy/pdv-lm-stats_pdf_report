FROM public.ecr.aws/lambda/python:3.9

LABEL MAINTAINER="msanz@identy.io"

COPY . ./

# Hack to install chromium dependencies
#RUN yum install -y -q unzip
#RUN yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm

# Install Chromium
#COPY ./tmp/headless-chromium /tmp/headless-chromium
#RUN /usr/bin/bash /tmp/install_browser.sh

RUN pip3 install --no-cache-dir -r requirements.txt

#RUN python3 -c "import pyppeteer; pyppeteer.chromium_downloader.download_chromium()"
#RUN python3 export_dash_app_to_pdf.py .

CMD ["run_ocr_report.lambda_handler"]