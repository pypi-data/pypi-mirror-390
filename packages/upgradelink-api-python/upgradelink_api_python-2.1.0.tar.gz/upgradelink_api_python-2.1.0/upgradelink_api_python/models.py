# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import Any


class Config(TeaModel):
    def __init__(
        self,
        access_key: str = None,
        access_secret: str = None,
        protocol: str = None,
        endpoint: str = None,
    ):
        self.access_key = access_key
        self.access_secret = access_secret
        self.protocol = protocol
        self.endpoint = endpoint

    def validate(self):
        self.validate_required(self.access_key, 'access_key')
        self.validate_required(self.access_secret, 'access_secret')
        self.validate_required(self.protocol, 'protocol')
        self.validate_required(self.endpoint, 'endpoint')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.access_key is not None:
            result['accessKey'] = self.access_key
        if self.access_secret is not None:
            result['accessSecret'] = self.access_secret
        if self.protocol is not None:
            result['protocol'] = self.protocol
        if self.endpoint is not None:
            result['endpoint'] = self.endpoint
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('accessKey') is not None:
            self.access_key = m.get('accessKey')
        if m.get('accessSecret') is not None:
            self.access_secret = m.get('accessSecret')
        if m.get('protocol') is not None:
            self.protocol = m.get('protocol')
        if m.get('endpoint') is not None:
            self.endpoint = m.get('endpoint')
        return self


class UrlUpgradeRequest(TeaModel):
    def __init__(
        self,
        url_key: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.url_key = url_key
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.url_key, 'url_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.url_key is not None:
            result['urlKey'] = self.url_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('urlKey') is not None:
            self.url_key = m.get('urlKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class UrlUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        url_key: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.url_key = url_key
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.url_key, 'url_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.url_key is not None:
            result['urlKey'] = self.url_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('urlKey') is not None:
            self.url_key = m.get('urlKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class UrlUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: UrlUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = UrlUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class UrlVersionRequest(TeaModel):
    def __init__(
        self,
        url_key: str = None,
        version_code: int = None,
    ):
        self.url_key = url_key
        self.version_code = version_code

    def validate(self):
        self.validate_required(self.url_key, 'url_key')
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.url_key is not None:
            result['urlKey'] = self.url_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('urlKey') is not None:
            self.url_key = m.get('urlKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        return self


class UrlVersionDataResponse(TeaModel):
    def __init__(
        self,
        url_key: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.url_key = url_key
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.url_key, 'url_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.url_key is not None:
            result['urlKey'] = self.url_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('urlKey') is not None:
            self.url_key = m.get('urlKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class UrlVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: UrlVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = UrlVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class FileUpgradeRequest(TeaModel):
    def __init__(
        self,
        file_key: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.file_key = file_key
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.file_key, 'file_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_key is not None:
            result['fileKey'] = self.file_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fileKey') is not None:
            self.file_key = m.get('fileKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class FileUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        file_key: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.file_key = file_key
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.file_key, 'file_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_key is not None:
            result['fileKey'] = self.file_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fileKey') is not None:
            self.file_key = m.get('fileKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class FileUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: FileUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = FileUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class FileVersionRequest(TeaModel):
    def __init__(
        self,
        file_key: str = None,
        version_code: int = None,
    ):
        self.file_key = file_key
        self.version_code = version_code

    def validate(self):
        self.validate_required(self.file_key, 'file_key')
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_key is not None:
            result['fileKey'] = self.file_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fileKey') is not None:
            self.file_key = m.get('fileKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        return self


class FileVersionDataResponse(TeaModel):
    def __init__(
        self,
        file_key: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.file_key = file_key
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.file_key, 'file_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.file_key is not None:
            result['fileKey'] = self.file_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('fileKey') is not None:
            self.file_key = m.get('fileKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class FileVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: FileVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = FileVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class ApkUpgradeRequest(TeaModel):
    def __init__(
        self,
        apk_key: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.apk_key = apk_key
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.apk_key, 'apk_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.apk_key is not None:
            result['apkKey'] = self.apk_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('apkKey') is not None:
            self.apk_key = m.get('apkKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class ApkUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        apk_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        url_file_size: int = None,
        url_file_md_5: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.apk_key = apk_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.url_file_size = url_file_size
        self.url_file_md_5 = url_file_md_5
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.apk_key, 'apk_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.url_file_size, 'url_file_size')
        self.validate_required(self.url_file_md_5, 'url_file_md_5')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.apk_key is not None:
            result['apkKey'] = self.apk_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.url_file_size is not None:
            result['urlFileSize'] = self.url_file_size
        if self.url_file_md_5 is not None:
            result['urlFileMd5'] = self.url_file_md_5
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('apkKey') is not None:
            self.apk_key = m.get('apkKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('urlFileSize') is not None:
            self.url_file_size = m.get('urlFileSize')
        if m.get('urlFileMd5') is not None:
            self.url_file_md_5 = m.get('urlFileMd5')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class ApkUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: ApkUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = ApkUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class ApkVersionRequest(TeaModel):
    def __init__(
        self,
        apk_key: str = None,
        version_code: int = None,
    ):
        self.apk_key = apk_key
        self.version_code = version_code

    def validate(self):
        self.validate_required(self.apk_key, 'apk_key')
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.apk_key is not None:
            result['apkKey'] = self.apk_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('apkKey') is not None:
            self.apk_key = m.get('apkKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        return self


class ApkVersionDataResponse(TeaModel):
    def __init__(
        self,
        apk_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.apk_key = apk_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.apk_key, 'apk_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.apk_key is not None:
            result['apkKey'] = self.apk_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('apkKey') is not None:
            self.apk_key = m.get('apkKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class ApkVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: ApkVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = ApkVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class ConfigurationUpgradeRequest(TeaModel):
    def __init__(
        self,
        configuration_key: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.configuration_key = configuration_key
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.configuration_key, 'configuration_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.configuration_key is not None:
            result['configurationKey'] = self.configuration_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('configurationKey') is not None:
            self.configuration_key = m.get('configurationKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class ConfigurationUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        configuration_key: str = None,
        version_name: str = None,
        version_code: int = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
        content: Any = None,
    ):
        self.configuration_key = configuration_key
        self.version_name = version_name
        self.version_code = version_code
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content
        self.content = content

    def validate(self):
        self.validate_required(self.configuration_key, 'configuration_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')
        self.validate_required(self.content, 'content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.configuration_key is not None:
            result['configurationKey'] = self.configuration_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        if self.content is not None:
            result['content'] = self.content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('configurationKey') is not None:
            self.configuration_key = m.get('configurationKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        if m.get('content') is not None:
            self.content = m.get('content')
        return self


class ConfigurationUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: ConfigurationUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = ConfigurationUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class ConfigurationVersionRequest(TeaModel):
    def __init__(
        self,
        configuration_key: str = None,
        version_code: int = None,
    ):
        self.configuration_key = configuration_key
        self.version_code = version_code

    def validate(self):
        self.validate_required(self.configuration_key, 'configuration_key')
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.configuration_key is not None:
            result['configurationKey'] = self.configuration_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('configurationKey') is not None:
            self.configuration_key = m.get('configurationKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        return self


class ConfigurationVersionDataResponse(TeaModel):
    def __init__(
        self,
        configuration_key: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.configuration_key = configuration_key
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.configuration_key, 'configuration_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.configuration_key is not None:
            result['configurationKey'] = self.configuration_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('configurationKey') is not None:
            self.configuration_key = m.get('configurationKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class ConfigurationVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: ConfigurationVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = ConfigurationVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class TauriVersionRequest(TeaModel):
    def __init__(
        self,
        tauri_key: str = None,
        version_name: str = None,
        target: str = None,
        arch: str = None,
    ):
        self.tauri_key = tauri_key
        self.version_name = version_name
        self.target = target
        self.arch = arch

    def validate(self):
        self.validate_required(self.tauri_key, 'tauri_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.target, 'target')
        self.validate_required(self.arch, 'arch')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.tauri_key is not None:
            result['tauriKey'] = self.tauri_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.target is not None:
            result['target'] = self.target
        if self.arch is not None:
            result['arch'] = self.arch
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('tauriKey') is not None:
            self.tauri_key = m.get('tauriKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('target') is not None:
            self.target = m.get('target')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        return self


class TauriVersionDataResponse(TeaModel):
    def __init__(
        self,
        tauri_key: str = None,
        version_name: str = None,
        version_code: int = None,
        target: str = None,
        arch: str = None,
        description: str = None,
    ):
        self.tauri_key = tauri_key
        self.version_name = version_name
        self.version_code = version_code
        self.target = target
        self.arch = arch
        self.description = description

    def validate(self):
        self.validate_required(self.tauri_key, 'tauri_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.target, 'target')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.tauri_key is not None:
            result['tauriKey'] = self.tauri_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.target is not None:
            result['target'] = self.target
        if self.arch is not None:
            result['arch'] = self.arch
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('tauriKey') is not None:
            self.tauri_key = m.get('tauriKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('target') is not None:
            self.target = m.get('target')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class TauriVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: TauriVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = TauriVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class ElectronVersionRequest(TeaModel):
    def __init__(
        self,
        electron_key: str = None,
        version_name: str = None,
        platform: str = None,
        arch: str = None,
    ):
        self.electron_key = electron_key
        self.version_name = version_name
        self.platform = platform
        self.arch = arch

    def validate(self):
        self.validate_required(self.electron_key, 'electron_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.platform, 'platform')
        self.validate_required(self.arch, 'arch')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.electron_key is not None:
            result['electronKey'] = self.electron_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.platform is not None:
            result['platform'] = self.platform
        if self.arch is not None:
            result['arch'] = self.arch
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('electronKey') is not None:
            self.electron_key = m.get('electronKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('platform') is not None:
            self.platform = m.get('platform')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        return self


class ElectronVersionDataResponse(TeaModel):
    def __init__(
        self,
        electron_key: str = None,
        version_name: str = None,
        version_code: int = None,
        platform: str = None,
        arch: str = None,
        description: str = None,
    ):
        self.electron_key = electron_key
        self.version_name = version_name
        self.version_code = version_code
        self.platform = platform
        self.arch = arch
        self.description = description

    def validate(self):
        self.validate_required(self.electron_key, 'electron_key')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.platform, 'platform')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.electron_key is not None:
            result['electronKey'] = self.electron_key
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.platform is not None:
            result['platform'] = self.platform
        if self.arch is not None:
            result['arch'] = self.arch
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('electronKey') is not None:
            self.electron_key = m.get('electronKey')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('platform') is not None:
            self.platform = m.get('platform')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class ElectronVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: ElectronVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = ElectronVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class LnxUpgradeRequest(TeaModel):
    def __init__(
        self,
        lnx_key: str = None,
        arch: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.lnx_key = lnx_key
        self.arch = arch
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.lnx_key, 'lnx_key')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.lnx_key is not None:
            result['lnxKey'] = self.lnx_key
        if self.arch is not None:
            result['arch'] = self.arch
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('lnxKey') is not None:
            self.lnx_key = m.get('lnxKey')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class LnxUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        lnx_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        url_file_size: int = None,
        url_file_md_5: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.lnx_key = lnx_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.url_file_size = url_file_size
        self.url_file_md_5 = url_file_md_5
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.lnx_key, 'lnx_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.url_file_size, 'url_file_size')
        self.validate_required(self.url_file_md_5, 'url_file_md_5')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.lnx_key is not None:
            result['lnxKey'] = self.lnx_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.url_file_size is not None:
            result['urlFileSize'] = self.url_file_size
        if self.url_file_md_5 is not None:
            result['urlFileMd5'] = self.url_file_md_5
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('lnxKey') is not None:
            self.lnx_key = m.get('lnxKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('urlFileSize') is not None:
            self.url_file_size = m.get('urlFileSize')
        if m.get('urlFileMd5') is not None:
            self.url_file_md_5 = m.get('urlFileMd5')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class LnxUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: LnxUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = LnxUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class LnxVersionRequest(TeaModel):
    def __init__(
        self,
        lnx_key: str = None,
        arch: str = None,
        version_code: int = None,
    ):
        self.lnx_key = lnx_key
        self.arch = arch
        self.version_code = version_code

    def validate(self):
        self.validate_required(self.lnx_key, 'lnx_key')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.lnx_key is not None:
            result['lnxKey'] = self.lnx_key
        if self.arch is not None:
            result['arch'] = self.arch
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('lnxKey') is not None:
            self.lnx_key = m.get('lnxKey')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        return self


class LnxVersionDataResponse(TeaModel):
    def __init__(
        self,
        lnx_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.lnx_key = lnx_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.lnx_key, 'lnx_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.lnx_key is not None:
            result['lnxKey'] = self.lnx_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('lnxKey') is not None:
            self.lnx_key = m.get('lnxKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class LnxVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: LnxVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = LnxVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class WinUpgradeRequest(TeaModel):
    def __init__(
        self,
        win_key: str = None,
        arch: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.win_key = win_key
        self.arch = arch
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.win_key, 'win_key')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.win_key is not None:
            result['winKey'] = self.win_key
        if self.arch is not None:
            result['arch'] = self.arch
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('winKey') is not None:
            self.win_key = m.get('winKey')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class WinUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        win_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        url_file_size: int = None,
        url_file_md_5: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.win_key = win_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.url_file_size = url_file_size
        self.url_file_md_5 = url_file_md_5
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.win_key, 'win_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.url_file_size, 'url_file_size')
        self.validate_required(self.url_file_md_5, 'url_file_md_5')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.win_key is not None:
            result['winKey'] = self.win_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.url_file_size is not None:
            result['urlFileSize'] = self.url_file_size
        if self.url_file_md_5 is not None:
            result['urlFileMd5'] = self.url_file_md_5
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('winKey') is not None:
            self.win_key = m.get('winKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('urlFileSize') is not None:
            self.url_file_size = m.get('urlFileSize')
        if m.get('urlFileMd5') is not None:
            self.url_file_md_5 = m.get('urlFileMd5')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class WinUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: WinUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = WinUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class WinVersionRequest(TeaModel):
    def __init__(
        self,
        win_key: str = None,
        version_code: int = None,
        arch: str = None,
    ):
        self.win_key = win_key
        self.version_code = version_code
        self.arch = arch

    def validate(self):
        self.validate_required(self.win_key, 'win_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.arch, 'arch')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.win_key is not None:
            result['winKey'] = self.win_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.arch is not None:
            result['arch'] = self.arch
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('winKey') is not None:
            self.win_key = m.get('winKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        return self


class WinVersionDataResponse(TeaModel):
    def __init__(
        self,
        win_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.win_key = win_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.win_key, 'win_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.win_key is not None:
            result['winKey'] = self.win_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('winKey') is not None:
            self.win_key = m.get('winKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class WinVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: FileVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = FileVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class MacUpgradeRequest(TeaModel):
    def __init__(
        self,
        mac_key: str = None,
        arch: str = None,
        version_code: int = None,
        appoint_version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
    ):
        self.mac_key = mac_key
        self.arch = arch
        self.version_code = version_code
        self.appoint_version_code = appoint_version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key

    def validate(self):
        self.validate_required(self.mac_key, 'mac_key')
        self.validate_required(self.arch, 'arch')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.appoint_version_code, 'appoint_version_code')
        self.validate_required(self.dev_model_key, 'dev_model_key')
        self.validate_required(self.dev_key, 'dev_key')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mac_key is not None:
            result['macKey'] = self.mac_key
        if self.arch is not None:
            result['arch'] = self.arch
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.appoint_version_code is not None:
            result['appointVersionCode'] = self.appoint_version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('macKey') is not None:
            self.mac_key = m.get('macKey')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('appointVersionCode') is not None:
            self.appoint_version_code = m.get('appointVersionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        return self


class MacUpgradeDataResponse(TeaModel):
    def __init__(
        self,
        mac_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        url_path: str = None,
        url_file_size: int = None,
        url_file_md_5: str = None,
        upgrade_type: int = None,
        prompt_upgrade_content: str = None,
    ):
        self.mac_key = mac_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.url_path = url_path
        self.url_file_size = url_file_size
        self.url_file_md_5 = url_file_md_5
        self.upgrade_type = upgrade_type
        self.prompt_upgrade_content = prompt_upgrade_content

    def validate(self):
        self.validate_required(self.mac_key, 'mac_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.url_path, 'url_path')
        self.validate_required(self.url_file_size, 'url_file_size')
        self.validate_required(self.url_file_md_5, 'url_file_md_5')
        self.validate_required(self.upgrade_type, 'upgrade_type')
        self.validate_required(self.prompt_upgrade_content, 'prompt_upgrade_content')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mac_key is not None:
            result['macKey'] = self.mac_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.url_path is not None:
            result['urlPath'] = self.url_path
        if self.url_file_size is not None:
            result['urlFileSize'] = self.url_file_size
        if self.url_file_md_5 is not None:
            result['urlFileMd5'] = self.url_file_md_5
        if self.upgrade_type is not None:
            result['upgradeType'] = self.upgrade_type
        if self.prompt_upgrade_content is not None:
            result['promptUpgradeContent'] = self.prompt_upgrade_content
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('macKey') is not None:
            self.mac_key = m.get('macKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('urlPath') is not None:
            self.url_path = m.get('urlPath')
        if m.get('urlFileSize') is not None:
            self.url_file_size = m.get('urlFileSize')
        if m.get('urlFileMd5') is not None:
            self.url_file_md_5 = m.get('urlFileMd5')
        if m.get('upgradeType') is not None:
            self.upgrade_type = m.get('upgradeType')
        if m.get('promptUpgradeContent') is not None:
            self.prompt_upgrade_content = m.get('promptUpgradeContent')
        return self


class MacUpgradeResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: MacUpgradeDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = MacUpgradeDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class MacVersionRequest(TeaModel):
    def __init__(
        self,
        mac_key: str = None,
        version_code: int = None,
        arch: str = None,
    ):
        self.mac_key = mac_key
        self.version_code = version_code
        self.arch = arch

    def validate(self):
        self.validate_required(self.mac_key, 'mac_key')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.arch, 'arch')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mac_key is not None:
            result['macKey'] = self.mac_key
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.arch is not None:
            result['arch'] = self.arch
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('macKey') is not None:
            self.mac_key = m.get('macKey')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        return self


class MacVersionDataResponse(TeaModel):
    def __init__(
        self,
        mac_key: str = None,
        package_name: str = None,
        version_name: str = None,
        version_code: int = None,
        description: str = None,
    ):
        self.mac_key = mac_key
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code
        self.description = description

    def validate(self):
        self.validate_required(self.mac_key, 'mac_key')
        self.validate_required(self.package_name, 'package_name')
        self.validate_required(self.version_name, 'version_name')
        self.validate_required(self.version_code, 'version_code')
        self.validate_required(self.description, 'description')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.mac_key is not None:
            result['macKey'] = self.mac_key
        if self.package_name is not None:
            result['packageName'] = self.package_name
        if self.version_name is not None:
            result['versionName'] = self.version_name
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.description is not None:
            result['description'] = self.description
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('macKey') is not None:
            self.mac_key = m.get('macKey')
        if m.get('packageName') is not None:
            self.package_name = m.get('packageName')
        if m.get('versionName') is not None:
            self.version_name = m.get('versionName')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('description') is not None:
            self.description = m.get('description')
        return self


class MacVersionResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        trace_id: str = None,
        data: MacVersionDataResponse = None,
    ):
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.data = data

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.trace_id, 'trace_id')
        self.validate_required(self.data, 'data')
        if self.data:
            self.data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        if self.data is not None:
            result['data'] = self.data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        if m.get('data') is not None:
            temp_model = MacVersionDataResponse()
            self.data = temp_model.from_map(m['data'])
        return self


class AppReportRequestEventData(TeaModel):
    def __init__(
        self,
        launch_time: str = None,
        version_code: int = None,
        dev_model_key: str = None,
        dev_key: str = None,
        target: str = None,
        arch: str = None,
        download_version_code: int = None,
        upgrade_version_code: int = None,
        code: int = None,
    ):
        self.launch_time = launch_time
        self.version_code = version_code
        self.dev_model_key = dev_model_key
        self.dev_key = dev_key
        self.target = target
        self.arch = arch
        self.download_version_code = download_version_code
        self.upgrade_version_code = upgrade_version_code
        self.code = code

    def validate(self):
        self.validate_required(self.version_code, 'version_code')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.launch_time is not None:
            result['launchTime'] = self.launch_time
        if self.version_code is not None:
            result['versionCode'] = self.version_code
        if self.dev_model_key is not None:
            result['devModelKey'] = self.dev_model_key
        if self.dev_key is not None:
            result['devKey'] = self.dev_key
        if self.target is not None:
            result['target'] = self.target
        if self.arch is not None:
            result['arch'] = self.arch
        if self.download_version_code is not None:
            result['downloadVersionCode'] = self.download_version_code
        if self.upgrade_version_code is not None:
            result['upgradeVersionCode'] = self.upgrade_version_code
        if self.code is not None:
            result['code'] = self.code
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('launchTime') is not None:
            self.launch_time = m.get('launchTime')
        if m.get('versionCode') is not None:
            self.version_code = m.get('versionCode')
        if m.get('devModelKey') is not None:
            self.dev_model_key = m.get('devModelKey')
        if m.get('devKey') is not None:
            self.dev_key = m.get('devKey')
        if m.get('target') is not None:
            self.target = m.get('target')
        if m.get('arch') is not None:
            self.arch = m.get('arch')
        if m.get('downloadVersionCode') is not None:
            self.download_version_code = m.get('downloadVersionCode')
        if m.get('upgradeVersionCode') is not None:
            self.upgrade_version_code = m.get('upgradeVersionCode')
        if m.get('code') is not None:
            self.code = m.get('code')
        return self


class AppReportRequest(TeaModel):
    def __init__(
        self,
        event_type: str = None,
        app_key: str = None,
        timestamp: str = None,
        event_data: AppReportRequestEventData = None,
    ):
        self.event_type = event_type
        self.app_key = app_key
        self.timestamp = timestamp
        self.event_data = event_data

    def validate(self):
        self.validate_required(self.event_type, 'event_type')
        self.validate_required(self.app_key, 'app_key')
        self.validate_required(self.event_data, 'event_data')
        if self.event_data:
            self.event_data.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.event_type is not None:
            result['eventType'] = self.event_type
        if self.app_key is not None:
            result['appKey'] = self.app_key
        if self.timestamp is not None:
            result['timestamp'] = self.timestamp
        if self.event_data is not None:
            result['eventData'] = self.event_data.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('eventType') is not None:
            self.event_type = m.get('eventType')
        if m.get('appKey') is not None:
            self.app_key = m.get('appKey')
        if m.get('timestamp') is not None:
            self.timestamp = m.get('timestamp')
        if m.get('eventData') is not None:
            temp_model = AppReportRequestEventData()
            self.event_data = temp_model.from_map(m['eventData'])
        return self


class AppReportResponse(TeaModel):
    def __init__(
        self,
        code: int = None,
        msg: str = None,
        docs: str = None,
        trace_id: str = None,
    ):
        self.code = code
        self.msg = msg
        self.docs = docs
        self.trace_id = trace_id

    def validate(self):
        self.validate_required(self.code, 'code')
        self.validate_required(self.msg, 'msg')
        self.validate_required(self.docs, 'docs')
        self.validate_required(self.trace_id, 'trace_id')

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['code'] = self.code
        if self.msg is not None:
            result['msg'] = self.msg
        if self.docs is not None:
            result['docs'] = self.docs
        if self.trace_id is not None:
            result['traceId'] = self.trace_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('code') is not None:
            self.code = m.get('code')
        if m.get('msg') is not None:
            self.msg = m.get('msg')
        if m.get('docs') is not None:
            self.docs = m.get('docs')
        if m.get('traceId') is not None:
            self.trace_id = m.get('traceId')
        return self


