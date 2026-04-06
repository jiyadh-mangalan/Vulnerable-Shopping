import { useState } from "react";

type Props = {
  src?: string | null;
  alt: string;
  className?: string;
  heightClass?: string;
};

/** Renders product image from URL (e.g. Picsum); falls back if missing or load fails (offline lab). */
export default function ProductImage({
  src,
  alt,
  className = "",
  heightClass = "h-40",
}: Props) {
  const [failed, setFailed] = useState(false);
  if (!src || failed) {
    return (
      <div
        className={`${heightClass} w-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-gray-400 text-sm ${className}`}
      >
        No image
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={alt}
      className={`${heightClass} w-full object-cover ${className}`}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  );
}
