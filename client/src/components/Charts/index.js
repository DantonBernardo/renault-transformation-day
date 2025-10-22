import "./style.css";
import AvgColor from "../AvgColor";
import LatestGroupTime from "../LatestGroupTime";

export default function Charts() {
  return (
    <div className="charts-container">
      <AvgColor />
      <LatestGroupTime />
    </div>
  );
};