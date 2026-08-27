# WS-50-ESTRA initial tranche

Run `RUN-20260827-ws50-estra-luna` is the result-fixation packet for the
LUNA-OC14-07 / WS-50-ESTRA discovery and preservation tranche.

The source checkout was already dirty before this run. The modified README
and all 2.0/3.0 candidate files are inherited preservation surfaces. This
worker branch is isolated from that checkout and records evidence only until
semantic review establishes an admissible transport set.

Required boundaries:

- reproduce the guarded 69-test baseline;
- classify every candidate file without reset, deletion or absorption;
- retain the negative holdout result and the fact that CI includes zero;
- do not claim typed-history dominance, release readiness, publication or
  activation;
- shared Logion control remains read-only.

The machine packet is `RESULT_FIXATION_PACKET.json`. Subsequent evidence files
are added only within the declared write set.
