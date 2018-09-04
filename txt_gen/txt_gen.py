
set_port_txt = "ucli\n\
pm\n\
port-add 21/0 100G RS\n\
port-add 27/0 100G RS\n\
port-enb 21/0\n\
port-enb 27/0\n\
an-set 21/0 1\n\
an-set 27/0 1\n\
end"

enter_pd_txt = "pd-p4-acl-1"
acl_match_txt = "pd acl_1_1_acl_table add_entry acl_acl_table_hit ipv4_srcAddr 0.0.0.0 ipv4_srcAddr_mask 0.0.0.0 ipv4_dstAddr 0.0.0.0 ipv4_dstAddr_mask 0.0.0.0 tcp_srcPort 0 tcp_srcPort_mask 0 tcp_dstPort 0 tcp_dstPort_mask 0 priority 1 entry_hdl "
set_ipv4_txt = "pd ipv4forward_1_2_ipv4_forward_table add_entry ipv4forward_ipv4_forward_table_hit ipv4_dstAddr 10.0.1.2 ipv4_dstAddr_prefix_length 32 action_dstAddr 0x123456123456 action_port 168 entry_hdl 1"

class txt_gen_handler(object):
	def __init__(self, filename):
		self.output_fp = open(filename, 'w')
		self.output_fp.write('\n')

	def fp_write_line(self, str):
		self.output_fp.write(str)
		self.output_fp.write('\n')

	def fp_skip_line(self):
		self.fp_write_line('')

	def fp_close(self):
		self.output_fp.write('\n')
		self.output_fp.close()

def txt_gen_main(filename, input_entry_count=10):
	handler = txt_gen_handler(filename)

	handler.fp_write_line(set_port_txt)
	handler.fp_skip_line()
	handler.fp_write_line(enter_pd_txt)

	entry_count = input_entry_count
	for i in range(1, entry_count):
		n_base = i % 255
		n_count = (i - n_base) / 255 + 1
		entry_str = "pd acl_1_1_acl_table add_entry acl_acl_table_hit ipv4_srcAddr 10.0.0.%d ipv4_srcAddr_mask 255.255.255.255 ipv4_dstAddr 10.0.0.%d ipv4_dstAddr_mask 255.255.255.255 tcp_srcPort 0 tcp_srcPort_mask 0 tcp_dstPort 0 tcp_dstPort_mask 0 priority 1 entry_hdl %d" \
			%(n_base, n_count, i)
		handler.fp_write_line(entry_str)
		handler.fp_skip_line()

	handler.fp_write_line(acl_match_txt+str(entry_count))
	handler.fp_skip_line()

	handler.fp_write_line(set_ipv4_txt)
	handler.fp_write_line('exit')
	handler.fp_close()
	return

if __name__ == '__main__':
	x=[(10+20*i) for i in range(13)] + [350, 450, 650, 850, 1000]
	#x = [10]
	for i in x:
		txt_gen_main('./%d.txt' %(i), i)
