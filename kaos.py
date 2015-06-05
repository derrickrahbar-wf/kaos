import click
import os
import sys
import re

allowed_devices = ['eth0', 'eth1', 'eth2']
allowd_distributions = ['normal', 'pareto, paretonormal']

class NetworkConfig:
    base_delay_cmd = 'tc qdisc %s dev %s root netem delay %s'
    base_loss_cmd = 'tc qdisc %s dev %s root netem loss %s'
    base_corrupt_cmd = 'tc qdisc %s dev %s root netem corrupt %s'
    base_reorder_cmd = 'tc qdisc %s dev %s root netem gap %s delay %s'
    reset_queue = 'tc qdisc del dev %s root'

    def __init__(self, device, latency, target_bw, packet_loss, 
                 distribution, corrupt, reorder):
        self.cmds = []
        self.first_cmd = True
        self.parse_device(device)
        self.parse_latency(latency)
        self.parse_bw(target_bw)
        self.parse_packet_loss(packet_loss)
        self.parse_distribution(distribution)
        self.parse_corrupt(corrupt)
        self.parse_reorder(reorder)
        self.build_cmds()

    def queue_generator(self):
        yield("add")
        yield("change")
        yield("change")
        yield("change")

    def parse_device(self, device):
        if device in allowed_devices:
            self.device = device
        else:
            print "%s is not an acceptable device" % device
            sys.exit()

    def parse_latency(self, latency):
        self.latency = latency

    def parse_bw(self, target_bw):
        if re.search('[a-zA-Z]', target_bw) != None:
            print "%s is not an acceptable bandwidth" % target_bw
        else:
            self.target_bw = target_bw

    def parse_packet_loss(self, packet_loss):
        pl = packet_loss.replace('%', "")
        if re.search('[a-zA-Z]', packet_loss) != None:
            print "%s is not an acceptable packet loss" % packet_loss
        else:
            self.packet_loss = packet_loss

    def parse_distribution(self, distribution):
        if distribution == "" or distribution in allowd_distributions:
            self.distribution = distribution
        else:
            print "%s is not an acceptable distribution" % distribution
            sys.exit()

    def parse_corrupt(self, corrupt):
        c = corrupt.replace('%', "")
        if corrupt == "":
            self.corrupt = corrupt
        elif re.search('[a-zA-Z]', corrupt) != None:
            print "%s is not an acceptable corruption" % corrupt
        else:
            self.corrupt = corrupt

    def parse_reorder(self, reorder):
        if re.search('[a-zA-Z]', reorder) != None:
            print "%s is not an acceptable bandwidth" % reorder
        else:
            self.reorder = reorder

    def build_cmds(self):
        queue_status = self.queue_generator()
        self.cmds.append(self.reset_queue)
        if self.latency != "":
            self.cmds.append(self.base_delay_cmd%(queue_status.next(), self.device,
                                                  self.latency))
            if self.reorder != "":
                self.cmds.append(self.base_reorder_cmd%(queue_status.next(), self.device, 
                                                        self.reorder, self.latency))
        if self.packet_loss != "":
            loss_cmd = (self.base_loss_cmd%(queue_status.next(), self.device, 
                                            self.packet_loss))
            if self.distribution != "":
                loss_cmd += " distribution %s" % self.distribution
            self.cmds.append(loss_cmd)

        if self.corrupt != "":
            self.cmds.append(self.base_corrupt_cmd%(queue_status.next(), self.device,
                                                    self.corrupt))

    def run_commands(self):
        for cmd in self.cmds:
            os.system(cmd)


@click.command()
@click.option('--device', default="")
@click.option('--latency')
@click.option('--target_bw', default="")
@click.option('--packet_loss')
@click.option('--distribution', default="")
@click.option('--corrupt', default="")
@click.option('--reorder', default="")
@click.option('--reset', default="False")
def main(device, latency, target_bw, packet_loss, distribution,
         corrupt, reorder, reset):
    if reset == True:
        os.system('tc qdisc del dev %s root'%device)
    net_conf = NetworkConfig(device, latency, target_bw, packet_loss,
                            distribution, corrupt, reorder)
    net_conf.run_commands()

if __name__ == '__main__':
    main()
