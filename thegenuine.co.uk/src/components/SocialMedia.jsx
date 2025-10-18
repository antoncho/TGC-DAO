import Link from "next/link";
import clsx from "clsx";
import {
  BsFacebook,
  BsTwitter,
  BsGithub,
  BsYoutube,
  BsLinkedin,
} from "react-icons/bs";

export const SocialMediaProfiles = [
  {
    title: "YouTube",
    href: "https://www.youtube.com/@thegenuinecollective",
    icon: BsYoutube,
  },
  { title: "GitHub", href: "https://github.com/thegenuinecollective", icon: BsGithub },
  {
    title: "Facebook",
    href: "https://www.facebook.com/thegenuinecollective",
    icon: BsFacebook,
  },
  {
    title: "LinkedIn",
    href: "https://www.linkedin.com/company/thegenuinecollective/",
    icon: BsLinkedin,
  },
  {
    title: "X (Twitter)",
    href: "https://x.com/thegenuineco",
    icon: BsTwitter,
  },
];

const SocialMedia = ({ className, invert = false }) => {
  return (
    <ul
      role="list"
      className={clsx(
        "flex gap-x-10",
        invert ? "text-white" : "text-neutral-950",
        className
      )}
    >
      {SocialMediaProfiles.map((item) => (
        <li key={item.title}>
          <Link
            href={item.href}
            aria-label={item.title}
            className={clsx(
              "transition",
              invert ? "hover:text-neutral-200" : "hover:text-neutral-700"
            )}
          >
            <item.icon className="h-6 w-6 fill-current" />
          </Link>
        </li>
      ))}
    </ul>
  );
};

export default SocialMedia;
