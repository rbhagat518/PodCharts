import CompareClient from "./compare-client";

type Props = {
  searchParams?: { id1?: string; id2?: string };
};

export default function ComparePage({ searchParams }: Props) {
  return <CompareClient initialId1={searchParams?.id1} initialId2={searchParams?.id2} />;
}
