from baseapp_for_restapi_backend_with_swagger import FlaskRestSubclass
from TestHelperSuperClass import testHelperAPIClient, env
from baseapp_for_restapi_backend_with_swagger.AppObj import AppObjBaseClass

from flask_restx import fields
from flask import Flask, Blueprint, request


nonstandardEnv = {
  'APIAPP_MODE': 'DOCKER',
  'APIAPP_VERSION': 'TEST-3.3.3',
  'APIAPP_FRONTEND': '.',
  'APIAPP_APIURL': 'http://apiurlxxx',
  'APIAPP_FRONTENDURL': 'http:/dsfslfknfed',
  'APIAPP_APIDOCSURL': 'http://apiurlxxx/apidocs',
  'APIAPP_APIACCESSSECURITY': '[{ "type": "basic-auth" }]',
  'APIAPP_USERFORJOBS': 'root',
  'APIAPP_GROUPFORJOBS': 'root',
  'APIAPP_SKIPUSERCHECK': True,
}
class otherAppObjClass(AppObjBaseClass):
  def initOnce(self):
    internal_apidoc_prefix = '/nonstandard/apidocs'
    internal_api_prefix = '/nonstandard/api'
    internal_frontend_prefix = '/nonstandard/frontend'

    self.flaskAppObject = Flask(__name__)
    self.registerRedirectCorrection('/api', self.globalParamObject.apiurl)
    self.registerRedirectCorrection('/apidocs', self.globalParamObject.apidocsurl)
    self.registerRedirectCorrection('/frontend', 'http://UNKNOWN.com/abc/frontend')
    api_blueprint = Blueprint('api', __name__)

    self.flastRestPlusAPIObject = FlaskRestSubclass(api_blueprint,
      version='UNSET',
      title='DocJob Scheduling Server API',
      description='API for the DockJob scheduling server',
      doc=internal_apidoc_prefix + '/',
      default_mediatype='application/json'
    )
    self.flastRestPlusAPIObject.setExtraParams(
      self.globalParamObject.apidocsurl,
      self.globalParamObject.getAPIDOCSPath(),
      self.globalParamObject.overrideAPIDOCSPath,
      self.globalParamObject.getAPIPath(),
      internal_apidoc_prefix=internal_apidoc_prefix,
      internal_api_prefix=internal_api_prefix,
      internal_frontend_prefix=internal_frontend_prefix
    )

    self.flastRestPlusAPIObject.init_app(api_blueprint)

    self.flaskAppObject.register_blueprint(api_blueprint, url_prefix=internal_api_prefix)
    #registerWebFrontendAPI(self)
    #self.flaskAppObject.register_blueprint(webfrontendBP, url_prefix=internal_frontend_prefix)



class test_AppObjAPI(testHelperAPIClient):

  # Rmeoving swagger
  # def test_checkSwaggerJsonFiles(self):
  #   #Tests all locations for swagger files
  #   result = self.testClient.get('/api/swagger.json')
  #   self.assertEqual(result.status_code, 200, msg='/apis/swagger.json for api not present')
  #   result = self.testClient.get('/apidocs/swagger.json')
  #   self.assertEqual(result.status_code, 200, msg='/apidocs/swagger.json for apidocs not present')


  # Removing swagger
  # def test_docsIndexesPresent(self):
  #   #print("*********DEBUG RULE START*************")
  #   #for rule in self.appObj.flaskAppObject.url_map.iter_rules():
  #   #  print(rule)
  #   #print("*********DEBUG RULE END*************")
  #
  #   #Tests all locations for swagger files
  #   #  this verifys the templates
  #   result = self.testClient.get('/apidocs/')
  #   self.assertEqual(result.status_code, 200, msg='/apidocs/ not present')

  # Removing swagger
  # def test_checkStatics(self):
  #   #result = self.testClient.get('/apidocs/swaggerui/bower/swagger-ui/dist/css/typography.css')
  #   result = self.testClient.get('/apidocs/swaggerui/bower/swagger-ui/dist/swagger-ui.js')
  #
  #   self.assertEqual(result.status_code, 200, msg='Could not find sample static')


  def test_apidocs_redirect_bad_URLs(self):
    result = self.testClient.get('/apidocs')
    if (result.status_code != 301):
      self.assertEqual(result.status_code, 308, msg="return code should be 301 or 308")
    self.assertEqual(result.headers['location'], 'http://apiurlxxx/apidocs/')

    #/api/ is never registered so will never redirect badly
    #result = self.testClient.get('/api')
    #self.assertEqual(result.status_code, 301)
    #self.assertEqual(result.headers['location'], 'http://localhost:3033/api/')

    result = self.testClient.get('/frontend')
    if (result.status_code != 301):
      self.assertEqual(result.status_code, 308, msg="return code should be 301 or 308")
    self.assertEqual(result.headers['location'], env["APIAPP_FRONTENDURL"] + '/') #in redirect add a slash

  # removing swagger
  # def test_indexPointsToCorrectSwaggerJSON(self):
  #   result = self.testClient.get('/apidocs/')
  #   self.assertEqual(result.status_code, 200, msg='/apidocs/index.html from apidocs not present')
  #   idx_file = result.get_data(as_text=True)
  #   ## print(idx_file)
  #   self.assertNotEqual(idx_file.find('http://apiurlxxx/apidocs/swagger.json'),-1,msg='Could not find correct url for swagger.json in index')

  # remvoing swagger
  # def test_indexHasCorrectSwaggerWhenUsingNonDefaultLocations(self):
  #   self.appObj = otherAppObjClass()
  #   self.appObj.init(nonstandardEnv, serverStartTime = None, testingMode = True, serverinfoapiprefix=None)
  #   self.testClient = self.appObj.flaskAppObject.test_client()
  #   self.testClient.testing = True
  #
  #   result = self.testClient.get('/nonstandard/apidocs/')
  #   self.assertEqual(result.status_code, 200, msg='/nonstandard/apidocs/index.html from apidocs not present')
  #   idx_file = result.get_data(as_text=True)
  #   print(idx_file)
  #   self.assertNotEqual(idx_file.find('http://apiurlxxx/apidocs/swagger.json'),-1,msg='Could not find correct url for swagger.json in index')
