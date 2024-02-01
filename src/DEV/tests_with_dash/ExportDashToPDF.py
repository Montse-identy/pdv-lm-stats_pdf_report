import asyncio
import shutil
import sys
import os
import datetime

from pyppeteer import launch, executablePath


# To solve pyppeteer issues on ubuntu
# https://stackoverflow.com/questions/57217924/pyppeteer-errors-browsererror-browser-closed-unexpectedly

# Create lambda function
# https://www.youtube.com/watch?v=23fE57EFRK4 <- with HTTP service
# https://www.youtube.com/watch?v=u6rh4YzhrTg
# https://www.youtube.com/watch?v=lrEAu75zhNI

# https://stackoverflow.com/questions/68701732/running-a-selenium-webscraper-in-aws-lambda-using-docker
# https://medium.com/limehome-engineering/running-pyppeteer-on-aws-lambda-with-serverless-62313b3fe3e2 <-
# https://pinchoflogic.com/multiplepartfrom-data-aws-api-gateway-lambda <- How to creste a lambda


class ExportDashToPDF():

    def __init__(self, url, pdf_path):
        self.url = url
        self.pdf_path = pdf_path

    async def generate_pdf(self):
        print(f'Chromium executable: {executablePath()}')

        # For running in lambda, we need server executable
        source = './tmp/headless-chromium'
        target = '/tmp'
        if not os.path.exists(source):
            os.makedirs(target)
        shutil.copy(source, target)
        os.chmod("/tmp/headless-chromium", 0o755)

        browser = await launch(args=[
            "--no-sandbox",
            "--single-process",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-zygote",
        ],
            executablePath="/tmp/headless-chromium",
            userDataDir="/tmp"  # Needed as lambda blocks file creation not in /tmp
        )

        page = await browser.newPage()

        await page.goto(self.url)
        # await page.waitForSelector('body')
        await page.waitFor(4000)  # in ms

        await page.pdf({'path': self.pdf_path, 'format': 'A4'})
        #pdf_binary = await page.pdf({'format': 'A4'})

        await browser.close()

        print(f"PDF generated: {datetime.datetime.now()}")


if __name__ == '__main__':
    path = sys.argv[1]

    # Run the function
    # asyncio.get_event_loop().run_until_complete(generate_pdf('http://localhost:8050',
    #                                                         os.path.join(path, 'fingerBasicReport_beta1.pdf')))

    print("Running export")
    # host.docker.internal for mac and windows
    # asyncio.get_event_loop().run_until_complete(generate_pdf('http://172.17.0.1:8050',
    #                                                         os.path.join(path, 'fingerBasicReport_beta1.pdf')))
    export = ExportDashToPDF('http://127.0.0.1:8050/', path)
    asyncio.get_event_loop().run_until_complete(export.generate_pdf())
