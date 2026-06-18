export default function LoadingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3.5">
      <span className="text-xs text-slate-500 mr-1.5">Thinking</span>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-blue-500/70 animate-bounce"
          style={{ animationDelay: `${i * 0.18}s`, animationDuration: "0.9s" }}
        />
      ))}
    </div>
  );
}
