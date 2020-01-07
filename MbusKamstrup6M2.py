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


baudrate = 9600
ibt = meterbus.inter_byte_timeout(baudrate)
meterbus.debug(True)
primadd = 205

def main():
    with serial.serial_for_url('COM7',
        baudrate, 8, 'E', 1,
        inter_byte_timeout=ibt,
        timeout=1) as ser:
        if False == ping_address(ser, primadd, 0):
            sys.exit(1)
        meterbus.send_request_frame(ser, primadd)
        frame = meterbus.load(
            meterbus.recv_frame(ser))
        print(frame)
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
                'device_type_id':  frame.body.bodyHeader.measure_medium_field.parts[0],
                'records': recs
            }
        print(json.dumps(ydata, indent=4, sort_keys=True))
        t1 = ydata['records'][4]['value']
        t2 = ydata['records'][5]['value']
        Power = ydata['records'][10]['value']
        Flow = ydata['records'][10]['value']
        
        #print(json.dumps(ydata.records, indent=4, sort_keys=True))
            
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
