'''
Test the preflight options return values are correct
'''
import TestHelperSuperClass
import json
import copy
from baseapp_for_restapi_backend_with_swagger import uniqueCommaSeperatedListClass

httpOrigin = 'http://a.com'
TestService = '/frontend/'

#Origin can only have one value
## http://blog.crashtest-security.com/multiple-values-access-control-allow-origin

#@TestHelperSuperClass.wipd
class corsPreflight_helpers(TestHelperSuperClass.testHelperAPIClient):
  def findCORSReturnVals(self, origin):
    loginJSON = {}
    result2 = self.testClient.options(
      TestService,
      data=json.dumps(loginJSON), content_type='application/json',
      headers={"Origin": origin}
    )
    self.assertEqual(result2.status_code, 200, msg="Options request did not return 200")
    return result2.headers

class test_corsPreflightCorrectResponseToOptions(corsPreflight_helpers):
  def test_simpleCorsCall(self):
    a = self.findCORSReturnVals(httpOrigin)

    requiredOriginList = uniqueCommaSeperatedListClass(TestHelperSuperClass.env["APIAPP_COMMON_ACCESSCONTROLALLOWORIGIN"]).data
    for x in requiredOriginList:
      a = self.findCORSReturnVals(x)
      self.assertEqual(a.get("Access-Control-Allow-Origin"),x)

    a = self.findCORSReturnVals("http://h.com")
    self.assertEqual(a.get("Access-Control-Allow-Origin"),None)

    a = self.findCORSReturnVals("hyyp://i.com")
    self.assertEqual(a.get("Access-Control-Allow-Origin"),None)

    a = self.findCORSReturnVals("http://randomOrigin")
    self.assertEqual(a.get("Access-Control-Allow-Origin"),None)

    a = self.findCORSReturnVals(None)
    self.assertEqual(a.get("Access-Control-Allow-Origin"),None)

    a = self.findCORSReturnVals("")
    self.assertEqual(a.get("Access-Control-Allow-Origin"),None)
