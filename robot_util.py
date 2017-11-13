from __future__ import print_function
import time
import traceback
import ssl
import sys
if (sys.version_info > (3, 0)):
    import urllib.request as urllib2
else:
    import urllib2

def getWithRetry(url, secure=True):

    for retryNumber in range(2000):
        try:
            print("GET", url)
            if secure:
                response = urllib2.urlopen(url).read()
            else:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                response = urllib2.urlopen(url, context=ctx).read()
            break
        except:
            print ("could not open url", url)
            traceback.print_exc()
            time.sleep(2)

    return response
