import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import { evaluations } from "../data/mockData";

export default function EvaluatorDashboard() {
  return (
    <DashboardLayout
      role="evaluator"
      title="Evaluator Dashboard"
      subtitle="Review proposals using transparent, predefined scoring criteria."
    >
      <div className="review-table-wrap">
        <table className="review-table">
          <thead>
            <tr>
              <th>Startup</th>
              <th>Challenge</th>
              <th>Status</th>
              <th>Innovation</th>
              <th>Feasibility</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {evaluations.map((item, idx) => (
              <tr key={idx}>
                <td><strong>{item.startup}</strong></td>
                <td>{item.challenge}</td>
                <td>
                  <Badge tone={item.status === "Completed" ? "green" : "amber"}>
                    {item.status}
                  </Badge>
                </td>
                <td>{item.status === "Completed" ? "8/10" : "—"}</td>
                <td>{item.status === "Completed" ? "9/10" : "—"}</td>
                <td><button className="btn btn-soft">Review</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section className="panel evaluator-card">
        <p className="eyebrow">Scoring framework</p>
        <h2>Example evaluation</h2>

        {[
          ["Innovation", 8],
          ["Technical feasibility", 9],
          ["Scalability", 8],
          ["Cost effectiveness", 7],
          ["Expected impact", 9],
        ].map(([label, value]) => (
          <div className="score-row" key={label}>
            <span>{label}</span>
            <div className="score-input">
              {[1,2,3,4,5,6,7,8,9,10].map((n) => (
                <button key={n} className={n === value ? "selected" : ""}>{n}</button>
              ))}
            </div>
          </div>
        ))}

        <div className="total-score">
          <span>Calculated score</span>
          <strong>82 / 100</strong>
        </div>
      </section>
    </DashboardLayout>
  );
}
