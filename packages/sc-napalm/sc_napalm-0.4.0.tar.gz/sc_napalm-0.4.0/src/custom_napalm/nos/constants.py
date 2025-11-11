NS = {
    "dn-top": "http://drivenets.com/ns/yang/dn-top",
    "dn-sys": "http://drivenets.com/ns/yang/dn-system",
    "dn-sys-dns": "http://drivenets.com/ns/yang/dn-sys-dns",
    "dn-sys-ncp": "http://drivenets.com/ns/yang/dn-sys-ncp",
    "dn-platform": "http://drivenets.com/ns/yang/dn-platform",
    "dn-if": "http://drivenets.com/ns/yang/dn-interfaces",
    "dn-trans": "http://drivenets.com/ns/yang/dn-transceivers",
    "dn-lldp": "http://drivenets.com/ns/yang/dn-lldp",
    "dn-proto": "http://drivenets.com/ns/yang/dn-protocol",
}

FACTS_RPC_REQ = """<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.1">
  <filter>
    <drivenets-top xmlns="http://drivenets.com/ns/yang/dn-top">
      <system xmlns="http://drivenets.com/ns/yang/dn-system">
        <oper-items>
          <system-type/>
          <system-uptime/>
          <system-version/>
        </oper-items>
        <config-items>
          <name/>
        </config-items>
        <ncps xmlns="http://drivenets.com/ns/yang/dn-sys-ncp">
          <ncp>
            <config-items>
              <platform>
                <oper-items>
                  <serial-number/>
                </oper-items>
              </platform>
            </config-items>
          </ncp>
        </ncps>
        <dns xmlns="http://drivenets.com/ns/yang/dn-sys-dns">
          <config-items>
            <domain-name/>
          </config-items>
        </dns>
      </system>
      <interfaces xmlns="http://drivenets.com/ns/yang/dn-interfaces">
        <interface>
          <name/>
        </interface>
      </interfaces>
    </drivenets-top>
  </filter>
</get>
"""

OPTICS_RPC_REQ = """<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.1">
<filter>
  <drivenets-top xmlns="http://drivenets.com/ns/yang/dn-top">
    <interfaces xmlns="http://drivenets.com/ns/yang/dn-interfaces">
       <interface>
          <transceivers xmlns="http://drivenets.com/ns/yang/dn-transceivers">
            <oper-items>
              <digital-optical-monitoring/>
            </oper-items>
        </transceivers>
      </interface>
    </interfaces>
  </drivenets-top>
</filter>
</get>
"""

LLDP_NEIGH_RPC_REQ = """<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.1">
<filter>
	<drivenets-top xmlns="http://drivenets.com/ns/yang/dn-top">
    <protocols xmlns="http://drivenets.com/ns/yang/dn-protocol">
      <lldp xmlns="http://drivenets.com/ns/yang/dn-lldp">
        <interfaces>
          <interface>
            <neighbors>
              <neighbor/>
            </neighbors>
          </interface>
        </interfaces>
      </lldp>      
    </protocols>
	</drivenets-top>
</filter>
</get>
"""

INVENTORY_RPC_REQ = """<get xmlns="urn:ietf:params:xml:ns:netconf:base:1.1">
<filter>
  <drivenets-top xmlns="http://drivenets.com/ns/yang/dn-top">
    <interfaces xmlns="http://drivenets.com/ns/yang/dn-interfaces">
       <interface>
        <oper-items>
          <interface-speed/>
        </oper-items>
        <transceivers xmlns="http://drivenets.com/ns/yang/dn-transceivers">
          <oper-items>
            <form-factor/>
            <ethernet-pmd/>
            <vendor/>
            <vendor-part/>
            <serial-no/>
            <wavelength/>
          </oper-items>
        </transceivers>
      </interface>
    </interfaces>
  </drivenets-top>
</filter>
</get>
"""
