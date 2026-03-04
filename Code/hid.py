# hid.py

import usb_hid

def hid_gamepad():
    
    report_id = 0x04
    _report_length = 10
    
    _descriptor = bytes((
        0x05, 0x01,  # Usage Page (Generic Desktop Ctrls)
        0x09, 0x05,  # Usage (Game Pad)
        0xA1, 0x01,  # Collection (Application)
        0x85, 0x04,  #   Report ID (4)
        0x09, 0x30,  #   Usage (X)
        0x09, 0x31,  #   Usage (Y)
        0x09, 0x32,  #   Usage (Z)
        0x09, 0x33,  #   Usage (Rx)
        0x09, 0x34,  #   Usage (Ry)
        0x09, 0x35,  #   Usage (Rz)
        0x15, 0x00,  #   Logical Minimum (0)
        0x26, 0xFF, 0x00,  #   Logical Maximum (255)
        0x75, 0x08,  #   Report Size (8)
        0x95, 0x06,  #   Report Count (6)
        0x81, 0x02,  #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0x09, 0x39,  #   USAGE (Hat switch)
        0x15, 0x00,  #   LOGICAL_MINIMUM (0)
        0x25, 0x07,  #   LOGICAL_MAXIMUM (7)
        0x35, 0x00,  #   PHYSICAL_MINIMUM (0)
        0x46, 0x3B, 0x01,  #   PHYSICAL_MAXIMUM (315)
        0x65, 0x14,  #   UNIT (Eng Rot:Angular Pos)
        0x75, 0x04,  #   REPORT_SIZE (4)
        0x95, 0x01,  #   REPORT_COUNT (1)
        0x81, 0x42,  #   INPUT (Data,Var,Abs,Null)
        0x75, 0x04,  #   REPORT_SIZE (4)
        0x95, 0x01,  #   REPORT_COUNT (1)
        0x81, 0x03,  #   INPUT (Cnst,Var,Abs)
        0x05, 0x09,  #   Usage Page (Button)
        0x19, 0x01,  #   Usage Minimum (Button 1)
        0x29, 0x14,  #   Usage Maximum (Button 20)
        0x15, 0x00,  #   Logical Minimum (0)
        0x25, 0x01,  #   Logical Maximum (1)
        0x75, 0x01,  #   Report Size (1)
        0x95, 0x18,  #   Report Count (24)
        0x81, 0x02,  #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)   
        0xC0,        # End Collection
    ))
        
    return usb_hid.Device(
        report_descriptor=_descriptor,
        usage_page=0x01,  # same as USAGE_PAGE from descriptor above
        usage=0x05,  # same as USAGE from descriptor above
        report_ids=(report_id,),  # report ID defined in descriptor
        in_report_lengths=(_report_length,),  # length of reports to host
        out_report_lengths=(0,),  # length of reports from host
    )