import PageIntro from "@/components/PageIntro";

export const metadata = {
  title: "Blog",
  description: "Ideas, updates, and lessons learned from The Genuine Collective.",
};

const BlogPage = () => {
  return (
    <>
      <PageIntro eyebrow="Blog" title="Ideas, updates, and lessons learned">
        <p>
          Thoughts on Futurism, Science, AI, Data, Security, and Product delivery from our 
          Collective. Field notes from building real systems for real users.
        </p>
      </PageIntro>
    </>
  );
};

export default BlogPage;
