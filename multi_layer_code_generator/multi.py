
import sys
import string

# the timestamp to implement Topo sorting
global ts
ts = 0
node_list = []

class nf_node(object):
	def __init__(self, name):
		self.name = name
		self.adj_nodes = []
		self.layer = -1
		self.pos = -1
		self.time = -1

	def set_layer(self, layer_count, pos_count):
		self.layer = layer_count
		self.pos = pos_count
		return

	def add_next(self, next_node):
		self.adj_nodes.append(next_node)

	def get_next_node_count(self):
		return (len(self.adj_nodes))

	def is_branch(self):
		return (self.get_next_node_count > 1)

	def is_tail(self):
		return (self.get_next_node_count()==0)

	def print_code(self):
		return ('/* node:%s layer:%d pos:%d */\n' %(self.name, self.layer, self.pos))

	def print_graph(self):
		if self in node_list:
			# node_list.append(self)
			return
		global ts
		print self.print_code()
		for node in self.adj_nodes:
			node.print_graph()
		self.time = ts
		ts += 1
		node_list.append(self)
		return

	def __cmp__(self, other_node):
		return cmp(self.name, other_node.name)

root = nf_node('')
acl_1 = nf_node('acl1')
acl_2 = nf_node('acl2')
ttl_1 = nf_node('ttl_1')
ttl_2 = nf_node('ttl_2')
ttl_3 = nf_node('ttl_3')
ttl_4 = nf_node('ttl_4')
ttl_5 = nf_node('ttl_5')
ip_1 = nf_node('ip_1')

ttl_1.add_next(ip_1)
ttl_2.add_next(ip_1)
ttl_3.add_next(ip_1)
ttl_4.add_next(ip_1)
ttl_5.add_next(ip_1)

acl_1.add_next(ttl_1)
acl_1.add_next(ttl_2)
acl_1.add_next(ttl_3)

acl_2.add_next(ttl_4)
acl_2.add_next(ttl_5)

root.add_next(acl_1)
root.add_next(acl_2)


class Solution(object):
	def __init__(self, root_node):
		self.handle_multilayer(root_node)
		root_node.print_graph()
		print len(node_list)
		node_list.sort(cmp=lambda x,y:cmp(x.time, y.time), reverse=True)
		for node in node_list:
			print node.print_code(), node.time
		return

	def handle_multilayer(self, root_node):
		self.handle_multilayer_helper(root_node, 0, 0)
		return

	def handle_multilayer_helper(self, curr_node, curr_layer_count, curr_layer_pos):
		curr_node.set_layer(curr_layer_count, curr_layer_pos)
		if curr_node.is_branch():
			curr_pos = 0
			for node in curr_node.adj_nodes:
				curr_pos += 1
				self.handle_multilayer_helper(node, curr_layer_count+1, curr_pos)
		else:
			for node in curr_node.adj_nodes:
				self.handle_multilayer_helper(node, curr_layer_count, 0)
		return



if __name__ == '__main__':
	print(root.get_next_node_count())
	s = Solution(root)



