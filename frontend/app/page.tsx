import { StatusStrip } from "../components/StatusStrip";

const initialStatuses = {
  R: "Reçue",
  C: "Non évaluée",
  A: "Non soumise",
  D: "Non autorisée",
  V: "Provisoire",
};

export default function HomePage() {
  return (
    <>
      <h1>Suivi d'une demande</h1>
      <section className="card">
        <p>Décrivez votre demande en langage naturel. Aucune connaissance des modèles ou des règles n'est requise.</p>
        <StatusStrip statuses={initialStatuses} />
      </section>
      <section className="card">
        <h2>Prochaine action</h2>
        <p>Répondre aux questions de clarification, le cas échéant.</p>
      </section>
    </>
  );
}
