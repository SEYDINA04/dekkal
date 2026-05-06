import { Link } from "react-router";
import logoBlue from "@/assets/logo_web_blue.png";
import logoWhite from "@/assets/logo_web_white.png";

export function BrandMark({ light = false }: { light?: boolean }) {
  return (
    <Link to="/" className="flex items-center">
      <img
        src={light ? logoWhite : logoBlue}
        alt="Dëkkal"
        className="h-10 w-auto object-contain sm:h-12"
      />
    </Link>
  );
}
