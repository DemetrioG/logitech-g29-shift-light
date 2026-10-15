"""Lista dispositivos HID Logitech (VID 046d) para descobrir o PID do volante."""
import hid

found = False
for d in hid.enumerate(0x046D, 0):
    found = True
    print(f"PID {d['product_id']:04x} | {d['product_string']} | interface {d['interface_number']} | usage_page {d['usage_page']:04x}")
if not found:
    print("Nenhum dispositivo Logitech encontrado.")
