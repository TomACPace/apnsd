#!/bin/sh

if [ $# -lt 4 ]; then
    echo "Usage: <apple_certificates_file.p12>   <certificate_file.pem> <private_key_file.pem>  <private_key_file_unencrypted.pem>"
    echo
    echo "For help on push notifications look at this one:"
    echo "    http://stackoverflow.com/questions/809682/error-using-ssl-cert-with-php"
    echo 
    echo "    Essentially you need 2 certificates - the developer_identity to sign the"
    echo "    code that goes on the phone. And the apple push service developer/prod"
    echo "    identity - this is the one you export and then use as the cert and pkey"
    echo "    file for APNSD (NOT THE dev_identity certificate)."
    echo 
    echo "    Also use dev apns identity for dev and the prod one for distribution AND release."
    exit 1
fi

in_cert_file=$1
cert_file=$2
pkey_file=$3
pkey_file_unenc=$4

openssl pkcs12 -nokeys -clcerts -in $in_cert_file -out $cert_file
openssl pkcs12 -in $in_cert_file -out $pkey_file -nocerts
openssl rsa -in $pkey_file -out $pkey_file_unenc

