"""
Chay bo mo phong.
  Backfill lan dau : python -m simulator.run --profile calibration --days 182 --reset
  Them 1 ngay moi  : python -m simulator.run --profile calibration --days 1
Trang thai the gioi (ton kho, rating, khach hang, bo sinh so ngau nhien) luu sau moi lan chay,
nen sinh tang dan tung ngay cho ket qua giong het sinh mot lan.
"""
import argparse
import pickle
import shutil
import time

from . import config as C
from .exporters import Exporter
from .scenarios import ScenarioBook
from .world import World


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="calibration", choices=["calibration", "holdout", "live"])
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--reset", action="store_true", help="xoa du lieu da sinh cua profile nay va bat dau lai")
    args = ap.parse_args()

    profile_dir = C.DATA_DIR / args.profile
    state_path = profile_dir / "_simulator_state" / "world.pkl"
    if args.reset and profile_dir.exists():
        shutil.rmtree(profile_dir)

    exporter = Exporter(profile_dir, api_store=profile_dir / C.API_STORE_DIR if args.profile == "live" else None)
    if state_path.exists():
        world = pickle.load(open(state_path, "rb"))
        if args.profile == "live":
            # tap van hanh thu doc lai tep kich ban moi lan chay de cai them su co minh hoa cho cac ngay sap toi;
            # tap phat trien va tap kiem tra giu nguyen kich ban da luu de ket qua tai lap dung nhu luc danh gia
            world.reload_scenarios(ScenarioBook(args.profile))
            exporter.write_scenarios(world)
    else:
        world = World(ScenarioBook(args.profile))
        exporter.write_scenarios(world)

    t0 = time.time()
    for k in range(args.days):
        out = world.simulate_day()
        exporter.write_day(world, out)
        if (k + 1) % 14 == 0 or k == args.days - 1:
            print(f"[{args.profile}] da sinh toi {out['date']} (ngay thu {world.day_idx}) - {time.time() - t0:.0f}s")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    pickle.dump(world, open(state_path, "wb"))


if __name__ == "__main__":
    main()
