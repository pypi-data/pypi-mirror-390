import TestHelperSuperClass
import unittest
import json
import pytz
import datetime
import copy

serverInfo = {
      'Server': {
        'Version': TestHelperSuperClass.env['APIAPP_VERSION'],
        "APIAPP_APIDOCSURL": TestHelperSuperClass.env['APIAPP_APIDOCSURL'],
        "APIAPP_FRONTENDURL": TestHelperSuperClass.env['APIAPP_FRONTENDURL']
      },
      'Derived': None
}


#@TestHelperSuperClass.wipd
class test_api(TestHelperSuperClass.testHelperAPIClient):

  def test_getServerInfo(self):
    result = self.testClient.get('/api/info/serverinfo')
    self.assertEqual(result.status_code, 200, msg="Wrong response when calling /api/info/serverinfo")
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqual(resultJSON, serverInfo)

  def test_getServerInfoSpecialData(self):
    expected = copy.deepcopy(serverInfo)
    expected["Derived"] = {
      "test": "123"
    }
    TestHelperSuperClass.serverInfoExtra["ret"] = { "test": "123" }
    result = self.testClient.get('/api/info/serverinfo')
    self.assertEqual(result.status_code, 200, msg="Wrong response when calling /api/info/serverinfo")
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqual(resultJSON, expected)
