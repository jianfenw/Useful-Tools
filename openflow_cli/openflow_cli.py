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
            # flow table
            #self.install_match_vlan(ev.dp)
            #self.install_match_vlan_modify_vlan(ev.dp)
            #self.install_l2forwarding_rule(ev.dp)
            self.install_unicast_rule(ev.dp)
            #self.install_acl_rule(ev.dp)
            #self.install_pop_egress_vlan(ev.dp)

            # group table
            #self.install_modify_vlan(ev.dp)
            #self.install_untag_vlan(ev.dp)

    def install_rule_example(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Table 10
        fields = {}
        fields['in_port'] = 1
        fields['vlan_vid'] = (10, 8191)
        matches = dp.ofproto_parser.OFPMatch(**fields)
        """
		# Table 0
		fields = {}
		fields['in_port'] = 1
		fields['eth_dst'] = 'ff:ff:ff:ff:ff:ff'
		matches = dp.ofproto_parser.OFPMatch(**fields)
		"""
        instructions = []
        instructions.append(dp.ofproto_parser.OFPInstructionGotoTable(20))
        flow_mod = dp.ofproto_parser.OFPFlowMod(dp,
                                                cookie=0,
                                                cookie_mask=0,
                                                table_id=10,
                                                command=dp.ofproto.OFPFC_ADD,
                                                idle_timeout=0,
                                                hard_timeout=0,
                                                priority=0,
                                                buffer_id=0,
                                                out_port=dp.ofproto.OFPP_ANY,
                                                out_group=dp.ofproto.OFPG_ANY,
                                                flags=0,
                                                match=matches,
                                                instructions=instructions)

        dp.send_msg(flow_mod)
        DLOG.info("Message sent")
        DLOG.info(
            "==============================================================================="
        )

    def install_acl_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        fields = {}
        #fields['eth_type'] = 0x8000
        fields['eth_type'] = 0x8100
        fields['vlan_vid'] = (0x1002, 0x1fff)
        match = ofp_parser.OFPMatch()
        instructions = []
        """
        instructions.append(
            ofp_parser.OFPInstructionActions(ofp.OFPIT_CLEAR_ACTIONS, []))
        """
        actions = []
        actions.append(ofp_parser.OFPActionGroup(group_id=0xb0005))
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
        DLOG.info("ACL sent")

    def install_l2forwarding_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        fields = {}
        fields['eth_type'] = 0x0800
        fields['vlan_vid'] = (0x1001, 0x1fff)
        fields['eth_dst'] = ('00:01:02:03:04:05', 'ff:ff:ff:ff:ff:ff')
        match = ofp_parser.OFPMatch(**fields)
        instructions = []
        #actions = []
        #actions.append(ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 7))
        #instructions.append(
        #    ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        instructions.append(ofp_parser.OFPInstructionGotoTable(30))
        flow_mod = ofp_parser.OFPFlowMod(dp,
                                         cookie=0,
                                         cookie_mask=0,
                                         table_id=20,
                                         command=ofp.OFPFC_ADD,
                                         priority=1,
                                         out_port=ofp.OFPP_ANY,
                                         out_group=ofp.OFPG_ANY,
                                         match=match,
                                         instructions=instructions)
        dp.send_msg(flow_mod)
        DLOG.info("L2forwarding rule sent")

    def install_unicast_rule(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['eth_type'] = 0x0800
        #fields['vlan_vid'] = (0x1001, 0x1fff)
        fields['ipv4_dst'] = '10.0.1.3'
        match = ofp_parser.OFPMatch(**fields)

        # Add instructions
        instructions = []
        """
        actions = []
        actions.append(ofp_parser.OFPActionGroup(group_id=0xb0006))
        instructions.append(
            ofp_parser.OFPInstructionActions(ofp.OFPIT_WRITE_ACTIONS, actions))
        """
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
        DLOG.info("IPv4Forward sent")

    def install_match_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['in_port'] = 1
        fields['vlan_vid'] = (0x1001, 0x1fff)
        match = ofp_parser.OFPMatch(**fields)
        # Add actions
        instructions = [ofp_parser.OFPInstructionGotoTable(20)]
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

    def install_match_vlan_modify_vlan(self, dp):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        # Add matches
        fields = {}
        fields['in_port'] = 2
        fields['vlan_vid'] = (0x1001, 0x1fff)
        match = ofp_parser.OFPMatch(**fields)
        # Add actions
        instructions = []
        actions = []
        actions.append(ofp_parser.OFPActionSetField(vlan_vid=0x1002))
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

    def install_pop_egress_vlan(self, dp):
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
