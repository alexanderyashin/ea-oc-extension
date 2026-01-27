export function structuralCriticalityVector(args: {
  brOut: number;
  brIn: number;
  depthOut: number;
  depthIn: number;
  inReach: number;
  inDegree: number;
}): { vector: number[]; note: "lex" } {
  const vector = [args.brOut, args.brIn, args.depthOut, args.depthIn, args.inReach, args.inDegree];
  return { vector, note: "lex" };
}
