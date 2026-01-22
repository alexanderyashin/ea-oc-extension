Write-Host "=== PDF3 WITNESS PACK START ==="
python .\tools\run_witness.py --name success  --seed 19 --steps 30 --force_stop_at null --force_inertia_at none       --force_collapse_at none --force_recover_at none
python .\tools\run_witness.py --name inertia  --seed 11 --steps 40 --force_stop_at null --force_inertia_at 8,9,10,11 --force_collapse_at none --force_recover_at none
python .\tools\run_witness.py --name collapse --seed 13 --steps 40 --force_stop_at null --force_inertia_at none       --force_collapse_at 10   --force_recover_at none
python .\tools\run_witness.py --name stop     --seed 17 --steps 40 --force_stop_at 12   --force_inertia_at none       --force_collapse_at none --force_recover_at none
Write-Host "=== PDF3 WITNESS PACK END ==="
