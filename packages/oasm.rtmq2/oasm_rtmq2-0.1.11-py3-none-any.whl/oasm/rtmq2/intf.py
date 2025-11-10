"""
RTMQ v2 Interface Module

This module provides hardware communication interfaces for RTMQ v2,
featuring multi-threaded communication and network protocol support.

Key Features:
- Multi-threaded communication architecture
- Network protocol support (Ethernet, UDP)
- Enhanced hardware abstraction for RTMQ v2
- Advanced debugging and logging capabilities
- Flexible configuration system

Dependencies:
- veri: Simulation interface (optional)
- threading: Multi-threading support
- serial: UART communication (optional)
- pcap: Network packet capture (optional)
- PyD3XX: FTDI D3XX interface (optional)
- pyodide: Web assembly environment (optional)
"""

import os,sys,time
PYODIDE = 'pyodide' in sys.modules
if PYODIDE:
    import js,pyodide
try:
    import veri
    veri.lib = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','..','..','hdl','rtmq2',sys.platform)
except:
    pass
try:
    import threading
except:
    pass
try:    
    import serial, struct, ctypes
except:
    pass
try:    
    import pcap
except:
    pass
try:    
    import PyD3XX
except:
    pass
from . import bit_concat, bit_split, C_BASE, PL01, pack_frame, unpack_frame, run_cfg


class base_intf:
    """
    Base interface class for RTMQ v2 hardware communication.
    
    This class provides enhanced functionality for RTMQ v2 interfaces,
    including multi-threading, network protocol support, and advanced
    configuration management.
    
    Attributes:
        EXC_TAG: Exception tag identifier (0xFFFFF)
        LOG_TAG: Log tag identifier (0xFFFFE)
        open_cnt: Counter for open operations
        pad_byt: Padding byte configuration
        nod_adr: Node address identifier
        loc_chn: Local channel identifier
        info: Information dictionary
        data: Data storage dictionary
        oper: Operation dictionary
        dev_tot: Device timeout configuration
        verbose: Verbose mode flag
        thread: Thread management object
        
    Methods:
        __init__: Initialize base interface with default values
        start: Start the interface thread
    """
    
    EXC_TAG = 0xFFFFF
    LOG_TAG = 0XFFFFE

    def __init__(self):
        """Initialize RTMQ v2 base interface with comprehensive configuration."""
        self.open_cnt = 0
        self.pad_byt = 0
        self.nod_adr = 0xFFFF
        self.loc_chn = 1
        self.info = dict()
        self.data = dict()
        self.oper = dict()
        self.dev_tot = 0.1
        self.verbose = True
        self.thread = None
    
    def start(self, *args, **kwargs):
        """
        Start the interface communication thread.
        
        Args:
            *args: Positional arguments for thread configuration
            **kwargs: Keyword arguments for thread configuration
            
        Returns:
            None: If thread is already running
        """
        if self.thread and self.thread.running:
            return
        kwargs['target'] = kwargs.get('target',self.run)
        kwargs['name'] = self.__class__.__name__+'-'+kwargs.get('name',str(id(self)))
        kwargs['daemon'] = kwargs.get('daemon',True)
        self.thread = threading.Thread(*args,**kwargs)
        self.thread.start()

    def stop(self):
        """
        Stop the interface communication thread.
        
        Safely terminates the running communication thread by setting
        the running flag to False and waiting for thread completion.
        Cleans up the thread reference after termination.
        
        Returns:
            None
        """
        if self.thread is not None:
            self.thread.running = False
            self.thread.join()
            self.thread = None

    @classmethod
    def stop_all(cls):
        """
        Stop all interface threads of this class type.
        
        Class method that terminates all running threads belonging
        to this interface class. Useful for cleanup in multi-interface
        environments.
        
        Returns:
            None
        """
        for thread in threading.enumerate():
            if thread.name.startswith(cls.__name__):
                thread.running = False
                thread.join()

    def run(self):
        """
        Main interface communication loop.
        
        Implements the core communication protocol for RTMQ v2 interfaces,
        handling both sending and receiving of data frames. The method
        processes incoming frames according to their type (info, operation,
        or data) and routes them to the appropriate handler.
        
        Process:
        1. Initialize thread running state and message queue
        2. Open device if not already open
        3. Set communication timeout
        4. Enter main communication loop:
           - Send pending messages from FIFO queue
           - Receive incoming frames
           - Parse frame header and payload
           - Process frame based on flag type
        
        Returns:
            None
        """
        import time, queue
        self.thread.running = True
        self.thread.fifo = queue.SimpleQueue()
        if self.open_cnt == 0:
            self.open()
        self.set_timeout(self.dev_tot)
        buf = dict()
        while self.thread.running:
            try:
                self._dev_wr(self.thread.fifo.get(timeout=self.dev_tot))
            except queue.Empty:
                pass            
            frm = self._dev_rd()
            if frm is None:
                continue
            flg,chn,adr,tag,pld = unpack_frame(frm)
            if flg == 4:
                chn,adr,fin = self._proc_info(pld)
            else:
                chn,adr = tag>>16,tag&0xffff
                if adr == 0xffff:
                    adr,fin = self._proc_oper(chn,pld)
                else:
                    fin = self._proc_data(chn,adr,pld)

    def open(self):
        """
        Open the interface with reference counting.
        
        Manages device opening with a reference counter to ensure the device
        is only physically opened once, even if multiple open requests are made.
        This prevents resource leaks and allows for nested usage patterns.
        
        Returns:
            None
        """
        if self.open_cnt == 0:
            self.open_device()
        self.open_cnt += 1
    
    def close(self):
        """
        Close the interface with reference counting.
        
        Manages device closing with a reference counter to ensure the device
        is only physically closed when all references are released.
        This prevents premature closure when multiple components are using
        the same interface.
        
        Returns:
            None
        """
        self.open_cnt -= 1
        if self.open_cnt == 0:
            self.close_device()

    def __enter__(self):
        """
        Context manager entry point.
        
        Implements the __enter__ protocol for context manager support,
        allowing the interface to be used with 'with' statements.
        Automatically opens the device upon entering the context.
        
        Returns:
            self: The interface instance
        """
        self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point.
        
        Implements the __exit__ protocol for context manager support,
        allowing the interface to be used with 'with' statements.
        Automatically closes the device upon exiting the context,
        regardless of whether an exception occurred.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_value: Exception value if an exception occurred
            traceback: Traceback object if an exception occurred
            
        Returns:
            None
        """
        self.close()

    def open_device(self):
        """
        Open the physical device connection.
        
        Abstract method that must be implemented by derived classes to
        establish the actual hardware connection specific to the interface type.
        
        Raises:
            NotImplementedError: If not implemented by derived class
        """
        raise NotImplementedError()

    def close_device(self):
        """
        Close the physical device connection.
        
        Abstract method that must be implemented by derived classes to
        terminate the actual hardware connection specific to the interface type.
        
        Raises:
            NotImplementedError: If not implemented by derived class
        """
        raise NotImplementedError()

    def set_timeout(self, tout):
        """
        Set communication timeout.
        
        Abstract method that must be implemented by derived classes to
        configure the communication timeout for the specific interface type.
        
        Args:
            tout: Timeout value in seconds
            
        Raises:
            NotImplementedError: If not implemented by derived class
        """
        raise NotImplementedError()

    def _dev_wr(self, dat):
        """
        Write data to the physical device.
        
        Abstract method that must be implemented by derived classes to
        handle the low-level data writing to the specific hardware device.
        
        Args:
            dat: Data to be written to the device
            
        Raises:
            NotImplementedError: If not implemented by derived class
        """
        raise NotImplementedError()

    def _dev_rd(self):
        """
        Read data from the physical device.
        
        Abstract method that must be implemented by derived classes to
        handle the low-level data reading from the specific hardware device.
        
        Returns:
            Data read from the device
            
        Raises:
            NotImplementedError: If not implemented by derived class
        """
        raise NotImplementedError()

    def _proc_info(self, pld):
        """
        Process information frames received from the device.
        
        Handles information frames containing status, exception, or other
        device information. Extracts relevant data and stores it in the
        interface's information dictionary for later retrieval.
        
        Args:
            pld: Payload data containing information frame
            
        Returns:
            tuple: (channel, address, is_exception)
                channel: Communication channel identifier
                address: Node address
                is_exception: Boolean indicating if this is an exception frame
        """
        info,chn,adr = bit_split(pld[0],(12,4,16))
        buf = self.info.get((chn<<16)+adr,None)
        if buf is None:
            buf = {}
            self.info[adr] = buf
        buf[info] = pld[1]
        if info == 0:
            print(f"Node #{adr}.{chn}: Exception occurred with flag 0x{buf[0]:08X} at address {buf.get(1,0)}.")
        return chn,adr,info==0

    def _proc_data(self, chn, adr, pld):
        """
        Process data frames received from the device.
        
        Handles data frames containing actual payload data. Combines the
        channel and address to create a unique identifier and stores
        or appends the payload data to the interface's data dictionary.
        
        Args:
            chn: Communication channel identifier
            adr: Node address
            pld: Payload data to be processed
            
        Returns:
            None
        """
        adr += chn<<16
        buf = self.data.get(adr,None)
        if buf is None:
            self.data[adr] = pld
        else:
            buf += pld
        return False
        
    def _proc_oper(self, chn, pld):
        """
        Process operation frames received from the device.
        
        Handles operation frames that control the interface's behavior.
        Processes task completion notifications, running status updates,
        and executes registered operation callbacks when appropriate.
        
        Args:
            chn: Communication channel identifier
            pld: Payload data containing operation information
            
        Returns:
            tuple: (address, is_finalized)
                address: Operation address identifier
                is_finalized: Boolean indicating if the operation is complete
        """
        narg,adr = pld[0]>>16,pld[0]&0xffff
        buf = self.data.get((chn<<16)+adr,[])
        fin = False
        if pld[1] == 0:
            if narg == 0:
                if self.verbose:
                    print(f"Node #{adr}.{chn}: Task complete.")
                fin = True
            elif narg == 1:
                if self.verbose:
                    print(f"Node #{adr}.{chn}: Task running.")
        else:
            oper = self.oper.get(pld[1],None)
            if callable(oper):
                oper(buf if narg == 0 else buf[-narg:],run_cfg(self,[adr],chn=chn))
                if narg > 0:
                    self.data[(chn<<16)+adr] = buf[:-narg]
        return adr,fin

    def write(self, flg, chn, adr, tag, pld):
        """
        Write a frame to the device.
        
        Packs the provided parameters into a frame and sends it to the device.
        If a thread is active, the frame is queued for transmission; otherwise,
        it is sent directly to the device.
        
        Args:
            flg: Frame flag indicating frame type
            chn: Communication channel identifier
            adr: Address to write to
            tag: Tag identifier for the frame
            pld: Payload data to send
            
        Returns:
            None
        """
        wcad = C_BASE.RTLK["W_CHN_ADR"]
        wnad = C_BASE.RTLK["W_NOD_ADR"]
        wtag = C_BASE.RTLK["W_TAG_LTN"]
        npld = C_BASE.RTLK["N_FRM_PLD"]
        nhdr = C_BASE.RTLK["N_BYT"] - 4*npld
        hdr = None
        if isinstance(tag, int):
            hdr = bit_concat((flg,3),(chn,wcad),(adr,wnad),(tag,wtag)).to_bytes(nhdr,'big')
            tag = [tag] 
        lpd = len(pld)
        ltg = len(tag)
        if lpd % 2 == 1:
            pld += [0]
            lpd += 1
        dlt = lpd // 2 - ltg
        if dlt > 0:
            tag += [tag[-1]] * dlt
            ltg += dlt
        if hdr is None:
            hdr = [bit_concat((flg,3),(chn,wcad),(adr,wnad),(i,wtag)).to_bytes(nhdr,'big') for i in tag]
        pad = b"\x00" * self.pad_byt
        buf = bytearray()
        for i in range(ltg):
            #buf += pad + pack_frame(flg, chn, adr, tag[i], pld[i*2:i*2+2])
            buf += pad + (hdr[i] if type(hdr) is list else hdr)
            if PL01:
                buf += int(pld[2*i+1]).to_bytes(4,'big')
                buf += int(pld[2*i]).to_bytes(4,'big')
            else:
                buf += int(pld[2*i]).to_bytes(4,'big')
                buf += int(pld[2*i+1]).to_bytes(4,'big')
        self.data = dict()
        if self.thread and self.thread.running:
            self.thread.fifo.put(buf)
        else:
            self._dev_wr(buf)

    def read_raw(self, cnt):
        """
        Read raw data from the device.
        
        Reads a specified number of frames from the device and concatenates their payloads.
        If fewer frames are available than requested, returns whatever was read before timeout.
        
        Args:
            cnt: Number of frames to read
            
        Returns:
            list: Concatenated payloads from the read frames
        """
        payloads = []
        for i in range(cnt):
            frm = self._dev_rd()
            if frm is None:
                break
            flg, chn, adr, tag, pld = unpack_frame(frm)
            payloads += pld
        return payloads

    def flush(self):
        """
        Flush the device buffers by reading all available data.
        
        Sets a short timeout and reads a large number of frames to clear
        any pending data in the device buffers. This helps reset the
        communication state between operations.
        
        Returns:
            None
        """
        self.set_timeout(0.1)
        self.read_raw(3000)

    def monitor(self, nodes, tout):
        """
        Monitor specified nodes for completion within a timeout period.
        
        Continuously reads frames from the device, processes them, and checks
        if all specified nodes have completed their operations. Returns the
        collected data once all nodes have completed or the timeout expires.
        
        Args:
            nodes: List of node addresses to monitor
            tout: Timeout period in number of read attempts
            
        Returns:
            dict: Dictionary containing all collected data from monitored nodes
        """
        mon = set(nodes)
        self.set_timeout(self.dev_tot)
        tot_cnt = 0
        while len(mon):
            frm = self._dev_rd()
            if frm is None:
                tot_cnt += 1
                if tot_cnt == tout:
                    break
                else:
                    continue
            flg,chn,adr,tag,pld = unpack_frame(frm)
            if flg == 4:
                chn,adr,fin = self._proc_info(pld)
            else:
                chn,adr = tag>>16,tag&0xffff
                if adr == 0xffff:
                    adr,fin = self._proc_oper(chn,pld)
                else:
                    fin = self._proc_data(chn,adr,pld)
            if fin:
                mon.remove(adr)
        return self.data
    
class uart_intf(base_intf):
    def __init__(self, port, baud=1000000):
        super().__init__()
        self.port = port
        self.baud = baud
        self.pad_byt = 0

    def open_device(self):
        self.dev = serial.Serial(self.port, self.baud)
        self.dev.stopbits = serial.STOPBITS_TWO
        self.set_timeout(1.0)

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev.timeout = tout
        self.dev.write_timeout = tout

    def _dev_wr(self, dat):
        self.dev.write(dat)
    
    def _dev_rd(self):
        frm = self.dev.read(C_BASE.RTLK["N_BYT"])
        if len(frm) == C_BASE.RTLK["N_BYT"]:
            return frm
        return None

class ft601_intf(base_intf):
    def __init__(self, sn):
        super().__init__()
        self.sn = sn
        self.pad_byt = (4 - C_BASE.RTLK["N_BYT"] % 4) % 4
        self.frm_byt = C_BASE.RTLK["N_BYT"] + self.pad_byt
        PyD3XX.SetPrintLevel(PyD3XX.PRINT_NONE)
    
    def open_device(self):
        sta, self.dev = PyD3XX.FT_GetDeviceInfoDetail(0)
        sta = PyD3XX.FT_Create(self.sn, PyD3XX.FT_OPEN_BY_SERIAL_NUMBER, self.dev)
        if sta != PyD3XX.FT_OK:
            raise RuntimeError(f"Incorrect serial number: {self.sn}")
        self.pipe = [0, 0]
        for i in range(2):
            sta, self.pipe[i] = PyD3XX.FT_GetPipeInformation(self.dev, 1, i)
            PyD3XX.FT_SetPipeTimeout(self.dev, self.pipe[i], 1000)

    def close_device(self):
        if self.dev is not None:
            PyD3XX.FT_Close(self.dev)
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def _dev_wr(self, dat):
        buf = PyD3XX.FT_Buffer.from_bytearray(dat)
        sta, bwr = PyD3XX.FT_WritePipe(self.dev, self.pipe[0], buf, len(dat), PyD3XX.NULL)
        if sta != PyD3XX.FT_OK:
            PyD3XX.FT_AbortPipe(self.dev, self.pipe[0])
            time.sleep(self.dev_tot)
            PyD3XX.FT_WritePipe(self.dev, self.pipe[0], buf, len(dat), PyD3XX.NULL)
    
    def _dev_rd(self):
        sta, buf, byt = PyD3XX.FT_ReadPipe(self.dev, self.pipe[1], self.frm_byt, PyD3XX.NULL)
        frm = buf.Value()
        if byt == self.frm_byt:
            vld = frm[self.pad_byt] >> 4
            if vld == 0:
                return frm
            time.sleep(self.dev_tot)
            return None
        time.sleep(self.dev_tot)
        PyD3XX.FT_AbortPipe(self.dev, self.pipe[1])
        buf = PyD3XX.FT_Buffer.from_bytes(b"\xFF"*self.frm_byt)
        PyD3XX.FT_WritePipe(self.dev, self.pipe[0], buf, self.frm_byt, PyD3XX.NULL)
        time.sleep(self.dev_tot)
        return None

class sim_intf(base_intf):
    def __init__(self, top='top', io=['LED'], trace=None):
        super().__init__()
        self.top = top.lower() if type(top) is str else top
        self.io = io
        self.trace = trace
        self.dev_tot = 0.001
        self.pad_byt = 0
        
    def open_device(self):
        if callable(self.top):
            self.dev = self.top()
        else:
            if PYODIDE:
                import json
                js.eval(f'veri.${self.top}=veri.top("rtmq2.{self.top}",{json.dumps(self.io)},self.trace,{C_BASE.RTLK["N_BYT"]})')
                self.dev = getattr(js.veri,f'${self.top}')
                self.dev.run()
            else:
                self.dev = veri.top(self.top,self.io,self.trace,C_BASE.RTLK['N_BYT'])
                self.dev.run()

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def _dev_wr(self, frm):
        self.dev.write(frm)
        
    def _dev_rd(self):
        frm = self.dev.read(C_BASE.RTLK['N_BYT'], self.dev_tot)
        if PYODIDE:
            frm = frm.to_py()
        return frm if len(frm) == C_BASE.RTLK['N_BYT'] else None
    
    def uart(self, port, baud=1000000):
        """
        Connect simulation interface to UART port.
        
        Creates a bidirectional bridge between the simulation device and a UART port,
        forwarding data in both directions. This allows the simulation to communicate
        with external devices via a real serial port.
        
        Args:
            port: Serial port name
            baud: Baud rate for UART communication (default: 1000000)
            
        Returns:
            None: Runs indefinitely until KeyboardInterrupt
        """
        port = serial.Serial(port,baud)
        try:
            while True:
                if port.in_waiting > 0:
                    self.dev.write(port.read(port.in_waiting))
                else:
                    self.dev.run()
                byt = self.dev.read(1,0)
                if len(byt) > 0:
                    port.write(byt)
        except KeyboardInterrupt:
            port.close()
    
    # def eth(self, eth, dst=None):
    #     """
    #     Connect simulation interface to Ethernet.
    #     
    #     Creates a bidirectional bridge between the simulation device and an Ethernet interface,
    #     forwarding data in both directions. This allows the simulation to communicate
    #     with external devices via a real network connection.
    #     
    #     Args:
    #         eth: Ethernet interface name
    #         dst: Destination MAC address (optional)
    #         
    #     Returns:
    #         None: Runs indefinitely until KeyboardInterrupt
    #     """
    #     eth = eth_intf(eth,dst)
    #     eth.set_timeout(0)
    #     eth.__enter__()
    #     byt = b''
    #     try:
    #         while True:
    #             frm = eth.read()
    #             if len(frm):
    #                 flg, chn, adr, tag, pld = unpack_frame(frm)
    #                 self.dev.write(frm)
    #             else:
    #                 self.dev.run()
    #             byt += self.dev.read(1,0)
    #             if len(byt) == C_BASE.RTLK['N_BYT']:
    #                 eth.write(byt)
    #                 byt = b''
    #     except KeyboardInterrupt:
    #         eth.__exit__(0,0,0)


#! Need revision
"""
class eth_intf(base_intf):
    ETHERTYPE_CUSTOM = 0x88B5
    PADDING_SIZE = 32
    def __init__(self, eth, dst=None):
        import binascii
        if sys.platform == 'linux':
            import fcntl
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                info = fcntl.ioctl(s.fileno(),0x8927, struct.pack('256s',eth[:15].encode()))
                src = info[18:24]
        elif sys.platform.startswith('win'):
            guid,mac = os.popen(f"wmic nic where NetConnectionID='{eth}' get GUID,MACAddress /value").read().strip().split('\n\n')
            eth = r'\\Device\\NPF_' + guid.split('=')[1]
            src = binascii.unhexlify(mac.split('=')[1].replace(':',''))
        self.eth = eth
        self.src = src
        self.dst = binascii.unhexlify(dst.replace(':','')) if dst else src
        self.dev_tot = 5
        super().__init__()

    def open_device(self):
        self.dev = pcap.pcap(name=self.eth,promisc=True,timeout_ms=1)#immediate=True)
        self.dev.setfilter(f'ether proto 0x{self.ETHERTYPE_CUSTOM:04x}')

    def close_device(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def set_timeout(self, tout):
        self.dev_tot = tout

    def write(self, frm):
        eth_header = self.dst+self.src+struct.pack('!H',self.ETHERTYPE_CUSTOM)
        padding = id(self.dev).to_bytes(8,'big') + b'\x00'*(self.PADDING_SIZE-8)
        n = asm.core.RTLK['N_BYT']
        for i in range(len(frm)//n):
            self.dev.sendpacket(eth_header+padding+frm[i*n:(i+1)*n])
                             
    def read(self):
        dev = self.dev
        pcap._pcap_ex.setup(dev._pcap__pcap)
        hdr  = pcap._pcap._pcap.pkthdr()
        phdr = ctypes.pointer(hdr)
        pkt  = ctypes.POINTER(ctypes.c_ubyte)()
        tout = self.dev_tot
        while True:
            n = pcap._pcap_ex.next_ex(dev._pcap__pcap,ctypes.byref(phdr),ctypes.byref(pkt))    
            if n == -2:
                raise EOFError
            elif n == -1:
                raise KeyboardInterrupt
            elif n == 1:
                hdr = phdr[0]
                ts = hdr.ts.tv_sec+(hdr.ts.tv_usec*dev._pcap__precision_scale)
                buf = ctypes.cast(pkt,ctypes.POINTER(ctypes.c_char*hdr.caplen))[0].raw
            #for ts, pkt in self.dev:
                if int.from_bytes(buf[12:14],'big') != self.ETHERTYPE_CUSTOM or int.from_bytes(buf[14:22],'big') == id(dev):
                    continue
                return buf[14+self.PADDING_SIZE:14+self.PADDING_SIZE+14]
            elif n == 0 and self.dev_tot == 0:
                return b''
            tout -= 0.001
            if tout <= 0:
                raise TimeoutError
"""

# if __name__ == '__main__':
#     intf = sim_intf()
#     with intf:
#         #intf.uart(sys.argv[1])
#         intf.eth(*sys.argv[1:])
