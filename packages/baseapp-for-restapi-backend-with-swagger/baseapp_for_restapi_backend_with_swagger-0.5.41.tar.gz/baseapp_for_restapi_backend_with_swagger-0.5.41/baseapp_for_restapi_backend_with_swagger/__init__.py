# -*- coding: utf-8 -*-

"""
    baseapp_for_restapi_backend_with_swagger
    ~~~~~~~~
    Python package which provides a base application class for an app with a restapi backend that provides a swagger
    :copyright: (c) 2018 by Robert Metcalf.
    :license: MIT, see LICENSE for more details.
"""

from .AppObj import AppObjBaseClass
from .requestHelper import getPaginatedParamValues
from .utils import from_iso8601
from .GlobalParamaters import GlobalParamatersClass, getInvalidEnvVarParamaterException, readFromEnviroment, getMissingVarFileException
from .FlaskRestSubclass import FlaskRestSubclass
from .apiSecurity import apiSecurityCheck, decodeJWTToken, DecodedTokenClass
from .uniqueCommaSeperatedList import uniqueCommaSeperatedListClass

from . import _version
__version__ = _version.get_versions()['version']
