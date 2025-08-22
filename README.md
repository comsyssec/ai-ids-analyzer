# AI-IDS-Analyzer: A Systematic Comparative Analysis Framework for AI-Based Intrusion Detection System

<img width="2368" height="1125" alt="ai-ids-analyzer" src="https://github.com/user-attachments/assets/8d549d83-62e3-4715-b3c3-5b8183851725" />


## Environment
1. You can run this program on the machine where you can run Python
  - This program is tested on Ubuntu 22.04 and Ubuntu 20.04

2. If you want to run this program on the Linux environment on the Windows machine, please install WSL2 (Windows Subsystem for Linux) on your Windows machine
`wsl --install` (in "명령 프롬프트")

## How to install the tester on the Linux machine
1. Install the following packages
  - `sudo apt-get install -y python3-pip`

2. Clone this repo on your local machine
  - `git clone https://github.com/comsyssec/ai-ids-analyzer.git`

3. Upgrade pip
  - `pip3 install --upgrade pip`

4. Install the Python packages
  - `pip3 install -r requirements.txt`

## How to run the tester
1. Run the AI-IDS-Analyzer
  - `python3 ai-ids-analyzer.py`

2. Run the IDS tester with options
  - You can find the options by typing the following command
  - `python3 ids-tester.py --help`

## How to Add Algorithms
 * You can add a new detector algorithm to the algorithms directory by python3 add_algorithm.py --name \<name of a new algorithm\> (e.g., `python3 add_algorithm.py --name decision_tree`)
 * You can add a new feature to the features directory by python3 add_feature.py --type \<flow/packet\> --name \<name of a new feature\> (e.g., `python3 add_feature.py --type flow --name iat`)
 * Please update a new setting by `python3 renew.py` when you add something

## Directories
* algorithms: the source codes of the classifiers
* definitions: the source codes of the abstract model definitions
* encoders: the source codes of encoders
* features: 40 features are included
* modules: the modules of IoTEDef
* scripts: the scripts for the experiments and the graphs
* utils: other functions defined

## Flow Features
### Description
 * forward_iat_std: the standard deviation of the inter-arrival time in the forward direction: True/False
 * flow_iat_total: the total inter-arrival time in the flow per window: True/False
 * flow_rst: the total number of the RST flags enabled in the flow per window: True/False
 * forward_iat_max: the maximum inter-arrival time of the flow per window: True/False
 * flow_packets_per_second: the number of packets per second of the flow per window: True/False
 * forward_packet_length_mean: the mean of the packet length in the forward direction: True/False
 * backward_packet_length_std: the standard deviation of the packet length in the backward direction: True/False
 * flow_ece: the total number of the ECE flags enabled in the flow per window: True/False
 * flow_iat_mean: the mean of the inter-arrival time in the flow per window: True/False
 * backward_packet_length_mean: the mean of the packet length in the backward direction: True/False
 * forward_packet_length_min: the minimum of the packet length in the forward direction: True/False
 * forward_iat_total: the total inter-arrival time in the forward direction: True/False
 * backward_packet_length_min: the minimum of the packet length in the backward direction: True/False
 * backward_iat_mean: the mean of the inter-arrival time in the backward direction: True/False
 * flow_cwr: the total number of the CWR flags enabled in the flow per window: True/False
 * flow_iat_min: the minimum of the inter-arrival time: True/False
 * flow_iat_max: the maximum of the inter-arrival time: True/False
 * total_length_of_backward_packets: the total length of the packets in the backward direction: True/False
 * forward_packet_length_std: the standard deviation of the packet length in the forward direction: True/False
 * total_backward_packets: the total number of packets in the backward direction: True/False
 * backward_iat_total: the total inter-arrival time in the backward direction: True/False
 * total_length_of_forward_packets: the total length of the packets in the forward direction: True/False
 * bpkts_per_second: the number of packets per second in the backward direction: True/False
 * backward_iat_std: the standard deviation of the inter-arrival time in the backward direction: True/False
 * forward_packet_length_max: the maximum of the packet length in the forward direction: True/False
 * fpkts_per_second: the number of packets per second in the forward direction: True/False
 * total_fhlen: the total number of header length in the forward direction: True/False
 * forward_iat_mean: the mean of the inter-arrival time in the forward direction: True/False
 * flow_urg: the total number of the URG flags enabled in the flow per window: True/False
 * flow_ack: the total number of the ACK flags enabled in the flow per window: True/False
 * forward_iat_min: the minimum of the inter-arrival time in the forward direction: True/False
 * flow_iat_std: the standard deviation of the inter-arrival time: True/False
 * total_forward_packets: the total number of packets in the forward direction: True/False
 * flow_syn: the number of the SYN flags enabled in the flow per window: True/False
 * flow_psh: the number of the PSH flags enabled in the flow per window: True/False
 * total_bhlen: the total number of the header length in the backward direction: True/False
 * flow_fin: the number of the FIN flags enabled in the flow per window: True/False
 * backward_packet_length_max: the maximum of the packet length in the backward direction: True/False
 * backward_iat_max: the maximum of the inter-arrival time in the backward direction: True/False
 * backward_iat_min: the minimum of the inter-arrival time in the backward direction: True/False
 * flow_protocol: the protocol value of the flow: True/False
### Reference
 * Please refer to the following link for the detail:
   - https://github.com/ahlashkari/CICFlowMeter/blob/master/ReadMe.txt
 * [Under Review] Myeong-Ha Hwang, Jeonghyun Joo, Heewoon Kang, HyeJeong Jin, YooJin Kwon, Hyunwoo Lee*. AI-IDS-Analyzer: A Systematic Comparative Analysis Framework for AI-Based Intrusion Detection System. Computers & Security (SCIE, 2025)
