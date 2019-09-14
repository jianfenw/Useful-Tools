import sys
import logging

from ryu.base import app_manager
from ryu.controller import dpset
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

ryu_loggers = logging.Logger.manager.loggerDict


def ryu_logger_on(is_logger_on):
    for key in ryu_loggers.keys():
        ryu_logger = logging.getLogger(key)
        ryu_logger.propagate = is_logger_on


DLOG = logging.getLogger('ofdpa')
DLOG.setLevel(logging.DEBUG)


class LemurOpenFlowController(app_manager.RyuApp):
    _CONTEXTS = {'dpset': dpset.DPSet}
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LemurOpenFlowController, self).__init__(*args, **kwargs)

    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handler_datapath(self, ev):
        DLOG.info(
            "==============================================================================="
        )
        DLOG.info("EventDP")
        DLOG.info("Datapath Id: %i - 0x%x", ev.dp.id, ev.dp.id)
        DLOG.info(
            "==============================================================================="
        )

        if ev.enter:
            # group table
            #self.install_l2_interface_group(ev.dp, vlan_vid=0x00b, port_num=50)
            #self.install_l2_interface_group(ev.dp, vlan_vid=0x611, port_num=51)
            #self.install_l3_interface_group(ev.dp, group_table_idx=3, vlan_vid=0x611, port_num=51)
            #self.install_modify_vlan(ev.dp)
            #self.install_untag_vlan(ev.dp)

            # flow table
            #self.install_match_empty_vlan(ev.dp)
            #self.install_match_vlan(ev.dp, (1,1), (1,3))
            #self.install_match_vlan_modify_vlan(ev.dp)
            #self.install_termination_mac_rule(ev.dp, next_table='unicast')
            #self.install_termination_mac_rule(ev.dp, next_table='bridging')
            #self.install_unicast_rule(ev.dp)
            #self.install_bridging_rule(ev.dp)
            self.install_acl_rule(ev.dp)
            #self.install_pop_egress_vlan(ev.dp)


    # Examples start.
    def install_match_empty_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['in_port'] = 50
        fields['vlan_vid'] = 0
        match = ofp_parser.OFPMatch(**fields)

        # Add actions
        instructions = []
        actions = []
        next_vlan_vid = self.encode_nsh_to_vlan(1, 1)
        actions.append(ofp_parser.OFPActionSetField(vlan_vid=next_vlan_vid))
        instructions.append(ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions))
        # Sets up the next table ID.
        instructions.append(ofp_parser.OFPInstructionGotoTable(20))

        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=10,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("Match Empty VLAN rule sent")

    def install_match_vlan(self, dp, routing_info, next_routing_info):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        vlan_vid = self.encode_nsh_to_vlan(routing_info[0], routing_info[1])
        fields['in_port'] = 51
        fields['vlan_vid'] = (vlan_vid, 0x1fff)
        match = ofp_parser.OFPMatch(**fields)
        # Add actions
        instructions = []
        actions = []
        if next_routing_info:
            next_vlan_vid = self.encode_nsh_to_vlan(next_routing_info[0], next_routing_info[1])
            actions.append(ofp_parser.OFPActionSetField(vlan_vid=next_vlan_vid))
            instructions.append(ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions))
        # Sets up the next table ID.
        instructions.append(ofp_parser.OFPInstructionGotoTable(20))
        
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=10,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("Match VLAN rule sent")

    def encode_nsh_to_vlan(self, service_path_id, service_id):
        # encode: spi-si ==> 0x6-spi-si
        return 0x1000 | ((0x6 << 8) + (service_path_id << 4) + service_id)

    def decode_nsh_from_vlan(self, vlan_vid):
        # decode: 0x6-spi-si ==> spi-si
        if vlan_vid & 0xf00 != 0x600:
            return None

        service_id = vlan_vid - (vlan_vid & 0xff0)
        service_path_id = (vlan_vid - (vlan_vid & 0xf0f)) >> 4
        return (service_path_id, service_id)

    def install_match_vlan_modify_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['in_port'] = 2
        fields['vlan_vid'] = 0x0000
        #fields['vlan_vid'] = (0, 0x1000)
        match = ofp_parser.OFPMatch(**fields)
        # Add actions
        instructions = []
        actions = []
        actions.append(ofp_parser.OFPActionSetField(vlan_vid=0x1611))
        instructions.append(
            ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions))
        instructions.append(ofp_parser.OFPInstructionGotoTable(20))
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=10,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("Match VLAN sent")

    def install_termination_mac_rule(self, dp, next_table='bridging'):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        fields = {}
        if next_table == 'unicast':
            fields['eth_type'] = 0x0800
            fields['vlan_vid'] = (0x1611, 0x1fff)
            fields['eth_dst'] = ('00:00:00:00:00:01', 'ff:ff:ff:ff:ff:ff')
        elif next_table == 'bridging':
            fields['eth_type'] = 0x0800
            #fields['vlan_vid'] = (0x1611, 0x1fff)
            fields['eth_dst'] = ('00:00:00:00:00:10', 'ff:ff:ff:ff:ff:f0')

        match = ofp_parser.OFPMatch(**fields)
        instructions = []
        actions = []
        # The port can only be set to the controller port. The following action does not work.
        #actions.append(ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 7))
        #actions.append(ofp_parser.OFPActionGroup(group_id=0xb0005))
        #instructions.append(
        #    ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        if next_table == 'unicast':
            instructions.append(ofp_parser.OFPInstructionGotoTable(30))
        elif next_table == 'bridging':
            instructions.append(ofp_parser.OFPInstructionGotoTable(50))

        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=20,
                                         command=ofp.OFPFC_ADD,
                                         priority=0,
                                         out_port=ofp.OFPP_ANY,
                                         out_group=ofp.OFPG_ANY,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("Termination MAC rule sent")

    def install_unicast_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['eth_type'] = 0x0800
        fields['vlan_vid'] = (0x1611, 0x1fff)
        fields['ipv4_dst'] = '10.0.1.3'
        match = ofp_parser.OFPMatch(**fields)

        # Add instructions
        instructions = []
        actions = []
        # Note: Both actions do not work.
        # (1) Sets up the output port.
        #actions.append(ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 5))
        # (2) Sets up the group ID for L3 unicast group table.
        #actions.append(ofp_parser.OFPActionGroup(group_id=0x20000001))
        #instructions.append(
        #    ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))

        # Sets up the next table to be ACL for further processing.
        instructions.append(ofp_parser.OFPInstructionGotoTable(60))
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=30,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         out_port=ofp.OFPP_ANY,
                                         out_group=ofp.OFPG_ANY,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("IPv4Forward rule sent")

    def install_bridging_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['vlan_vid'] = (0x1001, 0x1fff)
        fields['eth_dst'] = ("00:00:00:00:00:05", "ff:ff:ff:ff:ff:ff")
        match = ofp_parser.OFPMatch(**fields)

        # Add instructions
        instructions = []
        actions = []
        # (1) Sets up the next table to be ACL for further processing.
        instructions.append(ofp_parser.OFPInstructionGotoTable(60))
        # (2) Sets up the group ID for L2 interface group table.
        actions.append(ofp_parser.OFPActionGroup(group_id=0xb0005))
        instructions.append(
            ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        # (3) Sets up the output port.
        #actions.append(ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 7))
        #instructions.append(
        #    ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=50,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("Bridging rule sent")

    def install_acl_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        fields = {}
        fields['eth_type'] = 0x0800
        fields['vlan_vid'] = 0x1011
        fields['ipv4_dst'] = '100.0.1.1'
        match = ofp_parser.OFPMatch(**fields)

        instructions = []
        # This instruction drops all packets.
        #instructions.append(
        #    ofp_parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS, []))
        actions = []
        actions.append(ofp_parser.OFPActionGroup(group_id=0x20000001))
        instructions.append(
            ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=60,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("ACL rule sent")

    def install_pop_egress_vlan(self, dp):
        # The Egress tables do not work because the OFDPA version does not support |actset_output|.
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['actset_output'] = 2
        fields['vlan_vid'] = 0x1001
        match = ofp_parser.OFPMatch(**fields)
        # Add actions
        instructions = [ofp_parser.OFPInstructionGotoTable(211)]
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=210,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         out_port=2,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)

    def install_l2_interface_group(self, dp, vlan_vid, port_num):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add buckets
        buckets = []
        actions0 = []
        actions0.append(ofp_parser.OFPActionOutput(port_num))
        bucket0 = ofp_parser.OFPBucket(weight=0,
                                       watch_port=ofp.OFPP_ANY,
                                       watch_group=ofp.OFPG_ANY,
                                       actions=actions0)
        buckets.append(bucket0)
        # Create the group mod
        group_id = self.compute_l2_interface_group_id(vlan_vid, port_num)
        group_mod = ofp_parser.OFPGroupMod(dp, ofp.OFPGC_ADD,
                                           ofp.OFPGT_INDIRECT, group_id,
                                           buckets)
        dp.send_msg(group_mod)
        DLOG.info("L2 Interface Group (%d) rule sent" %(group_id))

    def compute_l2_interface_group_id(self, vlan_vid, port_num):
        # For example, group_id=0x000b 0033
        # The first 4 bits represent the target |vlan_vid|.
        # The last 4 bits represent the targe |port_num|
        return (vlan_vid << 16) | (port_num)

    def install_l3_interface_group(self, dp, group_table_idx, vlan_vid, port_num):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add buckets
        buckets = []
        actions0 = []
        actions0.append(ofp_parser.OFPActionSetField(vlan_vid=(0x1000 | vlan_vid)))
        actions0.append(ofp_parser.OFPActionSetField(eth_src=('00:01:02:03:04:05')))
        actions0.append(ofp_parser.OFPActionSetField(eth_src=('00:00:00:00:00:01')))
        actions0.append(ofp_parser.OFPActionGroup(group_id=self.compute_l2_interface_group_id(vlan_vid, port_num)))
        bucket0 = ofp_parser.OFPBucket(weight=0,
                                       watch_port=ofp.OFPP_ANY,
                                       watch_group=ofp.OFPG_ANY,
                                       actions=actions0)
        buckets.append(bucket0)
        # Create the group mod
        group_mod = ofp_parser.OFPGroupMod(dp, ofp.OFPGC_ADD,
                                           ofp.OFPGT_INDIRECT, 0x20000000 | group_table_idx,
                                           buckets)
        dp.send_msg(group_mod)
        DLOG.info("L3 Interface Group (%d) rule sent" %(0x20000000 + group_table_idx))

    def install_modify_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add buckets
        buckets = []
        actions0 = []
        actions0.append(ofp_parser.OFPActionSetField(vlan_vid=11))
        actions0.append(ofp_parser.OFPActionOutput(5))
        bucket0 = ofp_parser.OFPBucket(weight=0,
                                       watch_port=ofp.OFPP_ANY,
                                       watch_group=ofp.OFPG_ANY,
                                       actions=actions0)
        buckets.append(bucket0)
        # Create the group mod
        group_mod = ofp_parser.OFPGroupMod(dp, ofp.OFPGC_ADD,
                                           ofp.OFPGT_INDIRECT, 0xb0005,
                                           buckets)
        dp.send_msg(group_mod)
        DLOG.info("Modify VLAN sent")

    def install_untag_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add buckets
        buckets = []
        actions0 = []
        actions0.append(ofp_parser.OFPActionPopVlan(type_=18, len_=8))
        actions0.append(ofp_parser.OFPActionOutput(6))
        bucket0 = ofp_parser.OFPBucket(weight=0,
                                       watch_port=ofp.OFPP_ANY,
                                       watch_group=ofp.OFPG_ANY,
                                       actions=actions0)
        buckets.append(bucket0)
        # Create the group mod
        group_mod = ofp_parser.OFPGroupMod(dp, ofp.OFPGC_ADD,
                                           ofp.OFPGT_INDIRECT, 0xb0006,
                                           buckets)
        dp.send_msg(group_mod)
        DLOG.info("Untag VLAN sent")


if __name__ == '__main__':
    pass
