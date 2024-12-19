cd ..
xcopy /y utils.py iqoption
cd iqoption
gcloud functions deploy deriv --trigger-http --no-allow-unauthenticated --runtime=python39 --entry-point=deriv --memory=256MB --timeout=60s