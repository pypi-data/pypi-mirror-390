GET_INVENTORY = {
    "_": """
    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
            <port>
                <port-id/>
                <ethernet>
                <oper-speed/>
                </ethernet>
                <transceiver>
                    <vendor-part-number/>
                    <vendor-serial-number/>
                    <connector-type/>
                    <type/>
                </transceiver>
            </port>
        </state>
    </filter>
    """
}
