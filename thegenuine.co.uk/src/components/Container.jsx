import clsx from "clsx";

const Container = ({ 
  as: Component = "div", 
  className, 
  children, 
  innerClassName 
}) => {
  return (
    <Component className={clsx("max-w-8xl mx-auto px-6 lg:px-8", className)}>
      <div className={clsx("max-w-2xl mx-auto lg:max-w-none bg-transparent", innerClassName)}>
        {children}
      </div>
    </Component>
  );
};

export default Container;