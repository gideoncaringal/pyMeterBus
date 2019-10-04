import serial
import time
import simplejson as json
import yaml
import sys

try:
    import meterbus
except ImportError:
    import sys
    sys.path.append('../')
    import meterbus

ibt = meterbus.inter_byte_timeout(2400)
meterbus.debug(True)

def main():
    with serial.serial_for_url('/dev/ttyUSB0',
        2400, 8, 'E', 1,
        inter_byte_timeout=ibt,
        timeout=1) as ser:
        if False == ping_address(ser, 3, 0):
            sys.exit(1)
        meterbus.send_request_frame_multi(ser, 3)
        frame = meterbus.load(
            meterbus.recv_frame(ser))
        
        if frame is not None:
            recs = []
            for rec in frame.records:
                recs.append({
                    'value': rec.value,
                    'unit': rec.unit
                })
                

            ydata = {
                'manufacturer': frame.body.bodyHeader.manufacturer_field.decodeManufacturer,
                'identification': ''.join(map('{:02x}'.format, frame.body.bodyHeader.id_nr)),
                'access_no': frame.body.bodyHeader.acc_nr_field.parts[0],
                'medium':  frame.body.bodyHeader.measure_medium_field.parts[0],
                'records': recs
            }
        #print(json.dumps(ydata, indent=4, sort_keys=True))
        Energy = ydata['records'][0]['value']
        meterbus.send_request_frame_multi(ser, 3,"\x68\x03\x03\x68\x53\x03\xb1\x05\x16")
        frame = meterbus.load(
            meterbus.recv_frame(ser))
        
        if frame is not None:
            recs = []
            for rec in frame.records:
                recs.append({
                    'value': rec.value,
                    'unit': rec.unit
                })
                

            ydata = {
                'manufacturer': frame.body.bodyHeader.manufacturer_field.decodeManufacturer,
                'identification': ''.join(map('{:02x}'.format, frame.body.bodyHeader.id_nr)),
                'access_no': frame.body.bodyHeader.acc_nr_field.parts[0],
                'medium':  frame.body.bodyHeader.measure_medium_field.parts[0],
                'records': recs
            }
        Power = ydata['records'][10]['value']
        print Energy
        print Power
            
def ping_address(ser, address, retries=5):
    for i in range(0, retries + 1):
        meterbus.send_ping_frame(ser, address)
        try:
            frame = meterbus.load(meterbus.recv_frame(ser, 1))
            if isinstance(frame, meterbus.TelegramACK):
                return True
        except meterbus.MBusFrameDecodeError:
            pass

    return False
    

if __name__ == '__main__':
    main()
