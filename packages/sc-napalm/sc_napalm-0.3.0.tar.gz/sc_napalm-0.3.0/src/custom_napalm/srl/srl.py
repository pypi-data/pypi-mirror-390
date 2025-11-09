from napalm_srl import NokiaSRLDriver, gnmi_pb2
from napalm_srl.srl import SRLAPI
import grpc

from ..base import SCBaseDriver

from ipaddress import IPv6Address

import logging


class SCSLRAPI(SRLAPI):
    """
    This override fixes an issue with IPv6 addresses embedded in URLs when talking
    over GRPCs. Not sure if it's moot with the various TLS
    """

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        super().__init__(hostname, username, password, timeout, optional_args)

        try:
            IPv6Address(hostname)
            self.target = f"[{hostname}]:{self.gnmi_port}"
        except ValueError:
            pass

    def open(self):
        """Implement the NAPALM method open (mandatory)"""

        # read the certificates
        certs = {}
        if self.tls_ca:
            certs["root_certificates"] = self._readFile(self.tls_ca)
        if self.tls_cert:
            certs["certificate_chain"] = self._readFile(self.tls_cert)
        if self.tls_key:
            certs["private_key"] = self._readFile(self.tls_key)

        # If not provided and 'insecure' flag is set, fetch CA cert from server
        if "root_certificates" not in certs and self.insecure:
            # Lazily import dependencies
            from cryptography import x509
            import ssl
            from cryptography.hazmat.backends import default_backend

            ssl_cert = ssl.get_server_certificate(
                (self.hostname, self.gnmi_port)
            ).encode("utf-8")
            certs["root_certificates"] = ssl_cert
            logging.warning(
                "Using server certificate as root CA due to 'insecure' flag, not recommended for production use"
            )
            if not self.target_name:
                ssl_cert_deserialized = x509.load_pem_x509_certificate(
                    ssl_cert, default_backend()
                )
                ssl_cert_common_names = (
                    ssl_cert_deserialized.subject.get_attributes_for_oid(
                        x509.oid.NameOID.COMMON_NAME
                    )
                )
                self.target_name = ssl_cert_common_names[0].value
                logging.warning(
                    f"ssl_target_name_override(={self.target_name}) is auto-discovered, should be used for testing only!"
                )

        credentials = grpc.ssl_channel_credentials(**certs)
        self._metadata = [("username", self.username), ("password", self.password)]

        # open a secure channel, note that this does *not* send username/pwd yet...
        self._channel = grpc.secure_channel(self.target, credentials=credentials)
        # self._channel = grpc.secure_channel(
        #     target=self.target,
        #     credentials=credentials,
        #     options=(("grpc.ssl_target_name_override", self.target_name),),
        # )

        if self._stub is None:
            self._stub = gnmi_pb2.gNMIStub(self._channel)
            # print("stub", self._stub)


class SCNokiaSRLDriver(NokiaSRLDriver, SCBaseDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing insecure connection for testing purposes
        """
        optional_args = optional_args if optional_args else {}
        optional_args["insecure"] = True
        optional_args["skip_verify"] = True

        # optional_args["tls_cert"] = "/home/aliebowitz/srl/client.pem"
        # optional_args["tls_key"] = "/home/aliebowitz/srl/client.key"
        optional_args["encoding"] = "JSON_IETF"
        # hostname = f"[{hostname}]"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

        self.device = SCSLRAPI(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

    def get_inventory(self):
        path = {"/interface"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        interfaces = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        return interfaces
