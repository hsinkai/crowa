#!/usr/bin/perl -w
#
## ETag-aware wget
## Uses wget to more politely retrieve HTTP based information
## DJ Adams
## Version 0+1b
#
## wget --header='If-None-Match: "3ea6d375;3e2eee38"' http://www.w3.org/
#
## Changes
## 0+1b 2003-02-03 dja added User-Agent string to wget call
## 0+1 original version
#
## http://www.w3.org/2001/12/rubyrdf/pack/tests/scutter/wget.pl
#
use strict;
my $cachedir = '/tmp/etagcache'; # change this if you want
#my $etagfile = "$cachedir/".unpack("H*", $ARGV[0]); 
my $etagfile = "$cachedir/".$ARGV[1];
my $etag = `cat $etagfile 2>/dev/null`;
#`echo '$etag' > $etagfile`;
$etag =~ s/\\"/"/g;
$etag =~ s/^etag: (.*?)\n$/$1/ and $etag = qq[--header='If-None-Match: $etag'];

my $com="wget -U 'blagg/0+4i+ (wget.pl/0+1b)' --timeout=60 -S --no-check-certificate --no-proxy --quiet $etag -O - $ARGV[0]";
print "Running: $com";

my ($headers, $body) = split(/\n\n/, `wget -U 'blagg/0+4i+ (wget.pl/0+1b)' --timeout=60 -S --no-check-certificate --no-proxy --quiet $etag -O - $ARGV[0]`, 2);
print "Got headers: $headers\n\n";
if (defined $body) {
  ($etag) = $headers =~ /^(etag:.*?)$/m;
  print "Return value etag: $etag";
  defined $etag and $etag =~ s/\"/\\\"/g, `echo '$etag' > $etagfile`;
  print "\n==========\n";
  `echo $body > $ARGV[1]`;
}
else {
  print "Cached.";
}

