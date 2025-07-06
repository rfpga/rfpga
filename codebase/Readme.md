# RFPGA

<details>
  <summary> ME_ISO </summary>

-   [bladeRF-openbts5.0.iso](https://rfagora.s3.us-east-1.amazonaws.com/image/ISO/ME_ISO/bladeRF-openbts5.0/bladeRF-openbts5.0.iso)
-   [en.iplinkme.iso](https://rfagora.s3.us-east-1.amazonaws.com/image/ISO/ME_ISO/en.iplinkme.iso)
-   [Openbts_v2.09_64.iso ](https://rfagora.s3.us-east-1.amazonaws.com/image/ISO/ME_ISO/Openbts_v2.09_64.iso)
-   [openbts_v3.09_52M.iso ](https://rfagora.s3.us-east-1.amazonaws.com/image/ISO/ME_ISO/openbts_v3.09_52M.iso)
-   [V10-mode-s-openbts2.8.iso](https://rfagora.s3.us-east-1.amazonaws.com/image/ISO/ME_ISO/V10-mode-s-openbts2.8.iso)

</details>

<details>
  <summary> OpenBTS Startup </summary>


```sh
sudo su
cd /usr/local/src/openbts-2.6Mamou/smqueue
./smqueue
```

```sh
sudo su
cd /usr/local/src/openbts-2.6 Mamou/apps
./Openbts
```

</details>


<details>
  <summary> USRP1 test </summary>

- testing whether the system is connected

```sh
usrp_probe
```

```sh
cd /usr/local/share/gnuradio/examples/usrp
./usrp_benchmark_usb.py
```

```sh
sudo su
cd /usr/local/share/gnuradio/examples/digital
./benchmark_tx.py –f 900M –T A
```

```sh
sudo su
cd /usr/local/share/gnuradio/examples/digital
./benchmark_rx.py –f 900M –R A
```

```sh
usrp_fft.py -f 900M -R A
```

</details>

<details>
  <summary> USRP1 burn eeprom </summary>

```sh
sudo su
cd /usr/local/src/gnuradio-3.3.0/usrp/host/apps
./burn-serial-number s=123456
```

```sh
sudo su
cd /usr/local/src/gnuradio-3.3.0/usrp/host/apps
./burn-db-eeprom -t rfx1800_mimo_b -A –f
```

</details>