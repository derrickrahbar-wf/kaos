import click
import os
import sys

allowed_devices = ['eth0', 'eth1', 'eth2']
allowd_distributions = ['normal', 'pareto, paretonormal']

class NetworkConfig:
    base_delay_cmd = 'tc qdisc add dev %s root netem delay %s'
    base_loss_cmd = 'tc qdisc change dev %s root netem loss %s'

    def __init__(self, device, latency, target_bw, packet_loss, distribution):
        self.cmds = []
        self.parse_device(device)
        self.parse_latency(latency)
        self.parse_bw(target_bw)
        self.parse_packet_loss(packet_loss)
        self.parse_distribution(distribution)
        self.build_cmds()

    def parse_device(self, device):
        if device in allowed_devices:
            self.device = device
        else:
            print "%s is not an acceptable device" % device
            sys.exit()

    def parse_latency(self, latency):
        if re.search('[a-zA-Z]', latency) != None:
            print "%s is not an acceptable latency" % latency
        else:
            self.latency = latency

    def parse_bw(self, target_bw):
        if re.search('[a-zA-Z]', target_bw) != None:
            print "%s is not an acceptable bandwidth" % target_bw
        else:
            self.target_bw = target_bw

    def parse_packet_loss(self, packet_loss):
        if re.search('[a-zA-Z]', packet_loss) != None or packet_loss > 1:
            print "%s is not an acceptable packet loss" % packet_loss
        else:
            self.packet_loss = packet_loss

    def parse_distribution(self, distribution):
        if distribution == "" or distribution in allowd_distributions:
            self.distribution = distribution
        else:
            print "%s is not an acceptable distribution"
            sys.exit()

    def build_cmds():
        if self.latency != "":
            self.cmds.append(base_delay_cmd%(self.device, self.latency))
        if self.packet_loss != "":
            loss_cmd = (base_loss_cmd%(self.device, self.packet_loss))
            if self.distribution != "":
                loss_cmd += " distribution %s" % self.distribution
            self.cmds.append(loss_cmd)

    def run_cmds():
        for cmd in self.cmds:
            os.system(cmd)


@click.command()
@click.option('--device')
@click.option('--latency')
@click.option('--target_bw')
@click.option('--packet_loss')
@click.option('--distribution')
def main(device, latency, target_bw, packet_loss, distribution):
    net_conf = NetworkConfig(device, latency, target_bw, packet_loss, distribution)
    net_conf.run_commands()

if __name__ == '__main__':
    main()
