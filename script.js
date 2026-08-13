/* =========================================
   LOAD NAVIGATION
========================================= */

async function loadNavigation() {

    const navigation = document.getElementById("navigation");

    try {

        const response = await fetch("nav.html");

        if (!response.ok) {
            throw new Error("Navigation could not be loaded.");
        }

        navigation.innerHTML = await response.text();

    } catch (error) {

        console.error(error);

    }
}

/* =========================================
   LOAD EMPLOYMENT HISTORY
========================================= */

async function loadEmployment() {

    const container =
        document.getElementById("employment-list");

    try {

        const response = await fetch("employment.json");

        if (!response.ok) {
            throw new Error(
                "Employment history could not be loaded."
            );
        }

        const data = await response.json();


        data.employment.forEach((job) => {

            const element =
                document.createElement("article");

            element.className = "employment";


            element.innerHTML = `

                <div class="employment-heading">

                    <h3>
                        ${job.title}
                    </h3>

                    <p>
                        ${job.company} | ${job.date}
                    </p>

                </div>


                <ul>

                    ${job.responsibilities
                        .map(
                            (item) => `
                                <li>
                                    ${item}
                                </li>
                            `
                        )
                        .join("")}

                </ul>

            `;


            container.appendChild(element);

        });


    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <p>
                Employment history could not be loaded.
            </p>
        `;

    }
}
/* =========================================
   LOAD TECHNICAL SKILLS
========================================= */

async function loadTechnicalSkills() {

    const container =
        document.getElementById("technical-skill-list");

    try {

        const response = await fetch("projects.json");

        if (!response.ok) {
            throw new Error("Technical skills could not be loaded.");
        }

        const data = await response.json();


        data.technicalSkills.forEach((skill) => {

            const element = document.createElement("article");

            element.className = "technical-skill";


            element.innerHTML = `

                <div class="technical-skill-info">

                    <h3>
                        ${skill.title}
                    </h3>

                    <p>
                        ${skill.description}
                    </p>

                </div>


                <div class="technical-skill-media">

                    ${
                        skill.mediaType === "video"

                        ? `

                            <video
                                autoplay
                                muted
                                loop
                                playsinline
                                preload="metadata"
                            >

                                <source
                                    src="${skill.media}"
                                    type="video/mp4"
                                >

                            </video>

                        `

                        : `

                            <img
                                src="${skill.media}"
                                alt="${skill.title}"
                                loading="lazy"
                            >

                        `
                    }

                </div>

            `;


            container.appendChild(element);

        });


    } catch (error) {

        console.error(error);

        container.innerHTML = `
            <p>
                Technical skills could not be loaded.
            </p>
        `;

    }
}


/* =========================================
   START
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    loadNavigation();

    loadEmployment();

    loadTechnicalSkills();

});