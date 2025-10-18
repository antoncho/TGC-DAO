import clsx from "clsx";

function Office({ name, children, invert = false }) {
  return (
    <address
      className={clsx(
        "text-sm not-italic",
        invert ? "text-neutral-300" : "text-neutral-600"
      )}
    >
      <strong className={invert ? "text-white" : "text-neutral-950"}>
        {name}
      </strong>
      <br />
      {children}
    </address>
  );
}

const Offices = ({ invert = false, ...props }) => {
  return (
    <ul role="list" {...props}>
      <li>
        <Office name="London" invert={invert}>
          United Kingdom
          <br />
          Remote‑first hub
        </Office>
      </li>
      <li>
        <Office name="Manchester" invert={invert}>
          United Kingdom
          <br />
          Collaboration space
        </Office>
      </li>
      <li>
        <Office name="Remote" invert={invert}>
          GMT / CET friendly
          <br />
          Available worldwide
        </Office>
      </li>
    </ul>
    
  );
};

export default Offices;
