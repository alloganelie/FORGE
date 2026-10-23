type Axes = {
  R: string;
  C: string;
  A: string;
  D: string;
  V: string;
};

const AXIS_LABELS: Record<keyof Axes, string> = {
  R: "Demande",
  C: "Conformité",
  A: "Approbation",
  D: "Diffusion",
  V: "Version",
};

export function StatusStrip({ statuses }: { statuses: Axes }) {
  return (
    <section aria-label="Statuts séparés">
      <div className="strip">
        {(Object.keys(AXIS_LABELS) as (keyof Axes)[]).map((axis) => (
          <div className="axis" key={axis}>
            <b>{AXIS_LABELS[axis]}</b>
            <span>{statuses[axis]}</span>
          </div>
        ))}
      </div>
      <p className="provisional">Version provisoire — non finalisée.</p>
    </section>
  );
}
