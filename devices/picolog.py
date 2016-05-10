from ctypes import *

class Pico:
    def __init__(self, async=False):
        self.picolog=windll.PicoHRDL
        if not async:
            self.handle=self.picolog.HRDLOpenUnit()
        else:
            self.handle=self.picolog.HRDLOpenUnitAsync()
        if self.handle < 1:
            raise RuntimeError("Picolog failed to open. Try to turn it off and on again.")
        
    def closeUnit(self):#do not use. device is unable to start again. Just leave it at the end of meas.
        '''
        Shuts down a data logger unit.
        Arguments
        handle The handle, returned by HRDLOpenUnit, of the unit being closed
        Returns
        1 if a valid handle is passed
        0 if not
        '''
        self.picolog.HRDLCloseUnit(self.handle)
    
    def openUnitProgress(self):
        '''
        Checks the progress of an asynchronous open operation.

        Arguments
                    handle  Pointer to a short where the unit handle is to be written:
                            -1: if the unit fails to open
                            0: if no unit is found
                            >0:a handle to the device opened (this handle is not valid unless the function returns true)
                progress    Pointer to a short to which the percentage progress is to be written. 100%
                            implies that the open operation is complete
        Returns
                    0 if open operation is still in progress 
                    1 if the open operation is complete
        '''
        progress = c_short()
        
        self.picolog.HRDLOpenUnitProgress(self.handle, byref(progress))
        return progress.value

    def collectSingleValueAsync(self, channel, rng, conversionTime, singleEnded):
        """
        This function starts the unit sampling one value without blocking the calling
        application's flow.  Used in conjunction with HRDLGetSingleValueAsync and HRDLReady.

        Arguments
                handle  Handle returned by HRDLOpenUnit
                channel Channel number to convert.  If the channel is not valid then the
                        function will fail.
                range   The voltage range to be used.  If the range is not valid, the
                        function HRDLGetSingleValueAsync will return 0.
                conversionTime The time interval in which the sample should be converted.  If the
                        conversion time is invalid,the function HRDLGetSingleValueAsync
                        will fail and return 0.
                singleEnded The type of voltage to be measured: 
                                                                0: differential
                                                                nonzero: single-ended
        Returns
                1 if a valid handle is passed and the settings are correct
                0 if not
        """

        self.picolog.HRDLCollectSingleValueAsync(
            self.handle, channel, rng, conversionTime, singleEnded
            )

    def getMinMaxAdcCounts(self, channel):
        """
        This function returns the maximum and minimum ADC count available for the device
        referenced by handle.

        Arguments
                    handle  Handle returned by HRDLOpenUnit
                    minAdc  Pointer to a long, used to return the minimum ADC count available
                            for the unit referred to by handle
                    maxAdc  Pointer to a long, used to return the maximum ADC count available
                            for the unit referred to by handle
                    channel Channel number for which maximum and minimum ADC count are
                            required

        Returns
                    1 if a valid handle is passed
                    0 if not
        """
        minAdc = c_long()
        maxAdc = c_long()
        
        self.picolog.HRDLGetMinMaxAdcCounts(
            self.handle, byref(minAdc), byref(maxAdc), channel
            )
        
        return (maxAdc.value, minAdc.value)

    def getNumberOfEnabledChannels(self):
        """ 
        This function returns the number of analog channels enabled.

        Arguments
                handle Handle returned by HRDLOpenUnit
                nEnabledChannels    Pointer to a short, where the number of channels enabled will
                                    be written
        Returns
                1 if a valid handle is passed
                0 if not 
        """
        nEnabledChannels = c_short()
        
        self.picolog.HRDLGetNumberOfEnabledChannels(
            self.handle, byref(nEnabledChannels)
            )

        return nEnabledChannels.value

    def getSingleValue(self, channel, rng, conversionTime, singleEnded): 
        ################### reconfugures analog channel settings #############################    
        '''
        This function takes one sample for the specified channel at the selected voltage range
        and conversion time. 

        Arguments
                    handle Handle returned by HRDLOpenUnit.
                    channel The channel number to convert.ADC-20: 1 to 8 ADC-24: 1 to 16
                            If the channel is not valid then the function will fail and return 0.
                            range The voltage range to be used.  See HRDLSetAnalogInChannel for
                            possible values.  If the range is not valid, the function will return 0.
                    conversionTime  The time interval in which the sample should be converted.  See 
                                    HRDLSetInterval for possible values.  If the conversion time is
                                    invalid, the function will fail and return 0.
                    singleEnded The type of voltage to be measured.     0: differential
                                                                        nonzero: single-ended
                    overflow    Pointer to a bit field that indicates when the voltage on a channel
                                has exceeded the upper or lower limits.     Bit 0: Channel 1
                                                                                ...
                                                                            Bit 15: Channel 16
                    value       Pointer to a long where the ADC value will be written.
        Returns
                    1 if a valid handle is passed and settings are correct
                    0 if not
        If the function fails, call HRDLGetUnitInfo with info = HRDL_ERROR (7) to obtain the
        error code.  If the error code is HRDL_SETTINGS (5), then call HRDLGetUnitInfo again
        with info = HRDL_SETTINGS_ERROR (8) to determine the settings error.
        '''
        overflow = c_short()
        val = c_long()
        
        self.picolog.HRDLGetSingleValue(
            self.handle,
            channel,
            rng,
            conversionTime,
            singleEnded,
            byref(overflow),
            byref(val)
            )

        return (val.value, overflow.value)

    def getSingleValueAsync(self):
        '''
            This function retrieves the reading when the HRDLCollectSingleValueAsync has been called.

            Arguments
                        handle  Handle returned by HRDLOpenUnit
                        value   Pointer to a long where the ADC value will be written
                        overflow    Pointer to a value that indicates when the voltage on a channel has
                                    exceeded the upper or lower limits. Bit 0: Channel 1
                                                                                    ...
                                                                        Bit 15: Channel 16
            Returns
                        1 if a valid handle is passed and the function succeeds
                        0 if not
        '''
        val = c_long()
        overflow = c_short()
        
        self.picolog.HRDLGetSingleValueAsync(
            self.handle, byref(value), byref(overflow)
            )

        return (val.value, overflow.value)

    def getTimesAndValues(self, noOfValues):
        '''
        This function returns the requested number of samples for each enabled channel and
        the times when the samples were taken, so the values array needs to be (number of
        values) x (number of enabled channels). When one or more of the digital IOs are
        enabled as inputs, they count as one additional channel. The function informs the user
        if the voltages for any of the enabled channels have overflowed.

        Arguments
                    handle Handle returned by HRDLOpenUnit.
                    times Pointer to a long where times will be written.
                    values  Pointer to a long where sample values will be written. If more than
                            one channel is active, the samples are interleaved. If digital channels
                            are enabled then they are always the first values.  See table below
                            for the order in which data are returned.
                    overflow Pointer to a short indicating any inputs that have exceeded their
                            maximum voltage range.  Channels with overvoltages are indicated
                            by a high bit, with the LSB indicating channel 1 and the MSB channe l 16.
                    noOfValues The number of samples to collect for each active channel

        Returns
                    A non-zero number if successful indicating the number of values returned,
                    0 if the call failed or no values available

        Ordering of returned data (example)
        When two analog channels (e.g. 1 and 5) are enabled and a digital channel is set as
        an input, the data are returned in the following order:
            Sample No: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 . n-3 n-2 n-1
            Channel:   DI 1  5  DI 1  5  DI 1  5  DI 1  5  DI 1  5  . DI  1   5
        where n represents the value returned by the function and DI the digital inputs.
        The channels are always ordered from channel 1 up to the maximum channel number
        (ADC-24: channel 16, ADC-20: channel 8).  If one or more digital channels are set as
        inputs then the first sample contains the digital channels.  
        Digital inputs
        The digital channels are represented by a binary bit pattern with 0 representing off,
        and 1 representing on.  Digital input 1 is in bit 0
        '''
        times = c_long()
        vals = c_long()
        overflow = c_long()
        
        self.picolog.HRDLGetTimesAndValues(
            self.handle, byref(times), byref(vals), byref(overflow), noOfValues
            )

        return (times.value,vals.value,overflow.value)

    def getUnitInfo(self, info):
        '''
        info - int from 0 to 8, see manual
        
        This function writes information about the data logger to a character string. If the
        logger fails to open, only info = HRDL_ERROR (7) is available to explain why the last
        open unit call failed.  When retrieving the driver version, the handle value is ignored.

        Arguments
                    handle  Handle to the device from which information is required. If an invalid
                            handle is passed, the error code from the last unit that failed to open
                            is returned (as if info = HRDL_ERROR), unless info =
                            HRDL_DRIVER_VERSION and then the driver version is returned.
                    string  Pointer to the character string buffer in the calling function where the
                            unit information string (selected with info) will be stored. If a null
                            pointer is passed, no information will be written. 
                            stringLength Length of the character string buffer. If the string is not long enough
                            to accept all of the information, only the first stringLength
                            characters are returned.
                    info    Enumerated type (TABLE IN MANUAL) specifying what information is
                            required from the driver.

        Returns
                    The length of the string written to the character string buffer, string, by the function. 
                    If one of the parameters is out of range, or a null pointer is passed for string, the
                    function will return zero.
        '''

        buf = create_string_buffer(100)
        self.picolog.HRDLGetUnitInfo(self.handle, buf, 100, c_int(info))
        
        return buf.value

    def getValues(self, noOfValues):
        """
        This function returns the requested number of samples for each enabled channel, so
        the size of the values array needs to be (number of values) x (number of enabled
        channels). When one or more of the digital IOs are enabled as inputs, they count as
        one additional channel. The function informs the user if the voltages of any of the
        enabled channels have overflowed.

        Arguments
                    handle      Returned by HRDLOpenUnit.
                    values      Pointer to a long where the sample values are written. If more than
                                one channel is active, the samples are interleaved. If digital channels
                                are enabled then they are always the first value.  See table below for
                                the order in which data are returned.  
                    overflow    Pointer to a short indicating any inputs that have exceeded their
                                maximum voltage range.  Channels with overvoltages are indicated
                                by a high bit, with the LSB indicating channel 1 and the MSB channe l 16.
                    noOfValues  The number of samples to collect for each active channel

        Returns
                    A non-zero number if successful indicating the number of values returned, or
                    0 if the call failed or no values available

        Ordering of returned data (example)
        When two analog channels (e.g. 1 and 5) are enabled and a digital channel is set as
        an input, the data are returned in the following order.
            Sample No: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 . n-3 n-2 n-1
            Channel:   DI 1  5  DI 1  5  DI 1  5  DI 1  5  DI 1  5  . DI  1   5
        where n represents the value returned by the function and DI the digital inputs.
        The channels are always ordered from channel 1 up to the maximum channel number
        (ADC-24: channel 16, ADC-20: channel 8).  If one or more digital channels are set as
        inputs then the first sample contains the digital channels.  
        The digital channels are represented by a binary bit pattern with 0 representing off,
        and 1 representing on.  Digital input 1 is in bit 0.
        """
        overflow = c_short()
        vals = c_long()

        self.picolog.HRDLGetValues(
            self.handle, byref(vals), byref(overflow), noOfValues
            )

        return vals.value

    def ready (self):
        """
        This function indicates when the readings are ready to be retrieved from the driver.

        Arguments
                    handle Handle returned by HRDLOpenUnit.
        Returns
                    0 if not ready, or failed
                    1 if ready
        """
        return self.picolog.HRDLReady(self.handle)

    def run(self, nValues, method):
        """
        This function starts the device sampling and storing the samples in the driver's buffer.
 
        Arguments
                    handle  Handle returned by HRDLOpenUnit.
                    nValues Number of samples to collect for each active channel.
                    method  Sampling method.  This should be one of the values listed below.
        Returns
                    0 if failed, 
                    1 if successful
        Sampling methods
                    BM_BLOCK (0) Collect a single block and stop
                    BM_WINDOW (1) Collect a sequence of overlapping blocks
                    BM_STREAM (2) Collect a continuous stream of data
        """

        self.picolog.HRDLRun(handle, c_long(nValues), method)


    def setAnalogInChannel(self, channel, enabled, rng, singleEnded):
        '''
        This function enables or disables the selected analog channel.  If you wish to enable
        an odd-numbered channel in differential mode, you must first make sure that its
        corresponding even-numbered channel is disabled.  (For example, to set channel 1 to
        differential mode, first ensure that channel 2 is disabled.)

        Arguments
                    handle      Handle returned by HRDLOpenUnit.
                    channel     The channel that will be enabled or disabled. ADC-24: 1 to 16
                    enabled     Sets the channel active or dormant. 0: dormant
                                                                    <> 0: active
                    range       The voltage range to be used during sampling.  Applies only to
                                selected channel.  See Voltage ranges below.
                    singleEnded Non-zero to measure a single-ended voltage.
                                Zero for a differential voltage.

        Returns
                    0 if failed
                    1 if successful

        If the function fails, call HRDLGetUnitInfo with info = HRDL_SETTINGS_ERROR (8) to
        obtain the specific settings error.
            Voltage ranges  HRDL_2500_MV (0) 
                            HRDL_1250_MV (1) 
                            HRDL_625_MV(2) 
                            HRDL_313_MV (3) 
                            HRDL_156_MV (4) 
                            HRDL_78_MV (5) 
                            HRDL_39_MV (6) 
        '''
        
        self.picolog.HRDLSetAnalogInChannel(
            self.handle, channel, enabled, rng, singleEnded
            )

    def setDigitalIOChannel(
        self, directionOut, digitalOutPinState, enabledDigitalIn
        ):
        """
        Sets up the digital input/output channels.  If the direction is 'output' then the pin can
        be set high (on) or low (off).  While the device is sampling, the direction cannot be
        changed but the value of an output can.  

        Arguments
                    handle Handle returned by HRDLOpenUnit.
                    directionOut The directions of the digital IO pins, either input or output.  The
                    four least significant bits must be a combination of HRDL_DIGITAL_IO_CHANNEL constants.
                    digitalOutPinState  If the pin is set as an output, it can be set high or low by a
                                        combination of HRDL_DIGITAL_IO_CHANNEL constants (see below).
                    enabledDigitalIn    Sets the digital input as active.  Use a combination of 
                                        HRDL_DIGITAL_IO_CHANNEL constants (see below).
            Returns
                    0 if failed, 
                    1 if successful

        If the function fails, call HRDLGetUnitInfo with info = HRDL_SETTINGS_ERROR (8) to
        obtain the specific setting error.Pin values for directionOut, digitalOutPinState and enabledDigitalIn
        directionOut / enabledDigitalIn Description HRDL_DIGITAL_IO_CHANNEL_1 (1) IO Pin 1 
                                                    HRDL_DIGITAL_IO_CHANNEL_2 (2) IO Pin 2
                                                    HRDL_DIGITAL_IO_CHANNEL_3 (4) IO Pin 3
                                                    HRDL_DIGITAL_IO_CHANNEL_4 (8) IO Pin 4
        """
        self.picolog.HRDLSetDigitalIOChannel(
            self.handle, directionOut, digitalOutPinState, enabledDigitalIn
            )

    def setInterval(self, sampleInterval_ms, conversionTime):
        """
        This sets the sampling time interval.  The number of channels active must be able to
        convert within the specified interval.

        Arguments
                handle Handle returned by HRDLOpenUnit.
                sampleInterval_ms   Time interval in milliseconds within which all conversions must
                                    take place before the next set of conversions starts.
                                    conversionTime The amount of time given to one channel's conversion.  This
                                    must be one of the constants below.
        Returns
                0 if failed
                1 if successful

        If the function fails, call HRDLGetUnitInfo with info = HRDL_SETTINGS_ERRORS for the
        specific settings error.Conversion times
                                                    HRDL_60MS (0) 60 ms
                                                    HRDL_100MS (1) 100 ms
                                                    HRDL_180MS (2) 180 ms
                                                    HRDL_340MS (3) 340 ms
                                                    HRDL_660MS (4) 660 ms
        """

        self.picolog.HRDLSetInterval(
            self.handle, sampleInterval_ms, conversionTime
            )

   
    
    def setMains(self, reject):
        '''
        This function configures the mains noise rejection setting. Rejection takes effect the next time sampling occurs.

        Arguments
                    handle      Handle returned by HRDLOpenUnit.
                    sixtyHertz  Specifies whether 50 Hz or 60 Hz noise rejection is applied.  
                                                                                            0: reject 50Hz 
                                                                                            <> 0: reject 60 Hz
        Returns
                0 if failed
                1 if successful
        '''
        
        self.picolog.HRDLSetMains(self.handle, reject)

    def stop(self):
        self.picolog.HRDLStop(self.handle)

    def getVoltage(self, sample, Vmax, maxAdc):
        val = self.getSingleValue(sample[1], sample[2], sample[3], sample[4])[0]
        return val*Vmax/maxAdc
        
