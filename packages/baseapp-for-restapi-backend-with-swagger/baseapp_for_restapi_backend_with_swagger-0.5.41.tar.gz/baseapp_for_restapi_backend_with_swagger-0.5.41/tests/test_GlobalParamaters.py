from TestHelperSuperClass import testHelperSuperClass
from baseapp_for_restapi_backend_with_swagger import GlobalParamatersClass, getInvalidEnvVarParamaterException, readFromEnviroment, getMissingVarFileException
import json
##import os

class test_GlobalParamaters(testHelperSuperClass):
  appDir='.' #os.path.join('..','app')

  def test_acceptDEVELOPERMode(self):
    env = {
      'APIAPP_MODE': 'DEVELOPER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': '_',
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)

  def test_acceptDOCKERMode(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': '_',
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)

  def test_dontAcceptInvalidModeThrowsException(self):
    env = {
      'APIAPP_MODE': 'InvalidMode',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': '_',
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_MODE'))

  def test_webservicepathDosentExistThrowsException(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': '/a/b/c',
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_FRONTEND'))

  def test_missingVersionThrowsException(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': '',
      'APIAPP_FRONTEND': '_',
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_VERSION'))

  def test_validWebFrontendDirectory(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)

  def test_startupOutput(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getStartupOutput(), 'Mode:DOCKER\nVersion:TEST-1.2.3\nFrontend Location:' + self.appDir + '\napiurl:http://apiurl\napidocsurl:_\napiaccesssecurity:[]\n')

  def test_startupOutputWithAPIDOCSURL(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIDOCSURL': 'http://apidocsurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getStartupOutput(), 'Mode:DOCKER\nVersion:TEST-1.2.3\nFrontend Location:' + self.appDir + '\napiurl:http://apiurl\napidocsurl:http://apidocsurl\napiaccesssecurity:[]\n')

  def test_developerMode(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getDeveloperMode(), False)
    env = {
      'APIAPP_MODE': 'DEVELOPER',
      'APIAPP_VERSION': 'TEST-1.2.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurl',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getDeveloperMode(), True)

  def test_getWebServerInfoNoAuth(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    expRes = json.dumps({
        'version': 'TEST-3.3.3', #// Version show as 0 fom this file
        'apiurl': 'http://apiurlxxx',
        'apidocsurl': '_',
        'apiaccesssecurity': [] #// all supported auth types. Can be empty, or strings: basic-auth, jwt
        #// Empty list means no auth type
        #//  { type: basic-auth } - webfrontend will prompt user for username and password
        #//  ...
      })
    gp = GlobalParamatersClass(env)
    self.assertJSONStringsEqual(gp.getWebServerInfoJSON(), expRes);

  def test_getWebServerInfoBasicAuth(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx',
      'APIAPP_APIACCESSSECURITY': '[{ "type": "basic-auth" }]',
    }
    expRes = json.dumps({
        'version': 'TEST-3.3.3', #// Version show as 0 fom this file
        'apiurl': 'http://apiurlxxx',
        'apidocsurl': '_',
        'apiaccesssecurity': [{'type':'basic-auth'}] #// all supported auth types. Can be empty, or strings: basic-auth, jwt
        #// Empty list means no auth type
        #//  { type: basic-auth } - webfrontend will prompt user for username and password
        #//  ...
      })
    gp = GlobalParamatersClass(env)
    self.assertJSONStringsEqual(gp.getWebServerInfoJSON(), expRes);

  def test_invalidAPISecurityJSON(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx',
      'APIAPP_APIACCESSSECURITY': 'Some invalid JSON String',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_APIACCESSSECURITY'))

  def test_getAPIHost(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getAPIHost(), 'apiurlxxx')
    self.assertEqual(gp.getAPIPath(), '/aa/bb/cc')

  def test_getAPIHostWithPort(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.getAPIHost(), 'apiurlxxx:45')
    self.assertEqual(gp.getAPIPath(), '/aa/bb/cc')

  def test_PortOverride(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
    }
    gp = GlobalParamatersClass(env)
    self.assertEqual(gp.APIAPP_PORT, 3456)

  def test_InvalidPortOverride(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3DD456',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_PORT'))

  def test_ExceptionsMatchEvneWithDifferentMessages(self):
    expA = getInvalidEnvVarParamaterException('APIAPP_PORT')
    expB = getInvalidEnvVarParamaterException('APIAPP_PORT',messageOverride='TEST')
    self.assertEqual(expA, expB)
    
  def test_apiURLcanNotEndWithASlash(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc/',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
    }
    with self.assertRaises(Exception) as context:
      gp = GlobalParamatersClass(env)
    self.checkGotRightException(context,getInvalidEnvVarParamaterException('APIAPP_APIURL'))
    
  def test_readFromFile(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
      'APIAPP_SOMESTRINGFROMFILEXXFILE': './tests/envSingle'
    }
    self.assertEqual(readFromEnviroment(env, "APIAPP_SOMESTRINGFROMFILEXX", None, None, False),"Example Single Line Env File\n",msg="Wrong value read from file")
    
  def test_readFromFileNotExisting(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
      'APIAPP_SOMESTRINGFROMFILEXXFILE': '/a/b/c'
    }
    with self.assertRaises(Exception) as context:
      self.assertEqual(readFromEnviroment(env, "APIAPP_SOMESTRINGFROMFILEXX", None, None, False))
    self.checkGotRightException(context,getMissingVarFileException('APIAPP_SOMESTRINGFROMFILEXX','aa'))
  
  def test_readFromFileJSON(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
      'APIAPP_SOMESTRINGFROMFILEXXFILE': './tests/envSomeJSON'
    }
    self.assertEqual(readFromEnviroment(env, "APIAPP_SOMESTRINGFROMFILEXX", None, None, False),'{"Type": "SQLAlchemy","connectionString":"mysql+pymysql://dsafdsa:aaa@saddsa.eu-west-2.rds.amazonaws.com/dsffds","ssl_ca": "/rds-combined-ca-bundle.pem"}',msg="Wrong value read from file")
  
  def test_readFromFileMultiLine(self):
    env = {
      'APIAPP_MODE': 'DOCKER',
      'APIAPP_VERSION': 'TEST-3.3.3',
      'APIAPP_FRONTEND': self.appDir,
      'APIAPP_APIURL': 'http://apiurlxxx:45/aa/bb/cc',
      'APIAPP_APIACCESSSECURITY': '[]',
      'APIAPP_PORT': '3456',
      'APIAPP_SOMESTRINGFROMFILEXXFILE': './tests/envMultiLine'
    }
    self.assertEqual(readFromEnviroment(env, "APIAPP_SOMESTRINGFROMFILEXX", None, None, False),"Example Multi Line Env File\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n",msg="Wrong value read from file")
    
  
  #todo read multi line file
  