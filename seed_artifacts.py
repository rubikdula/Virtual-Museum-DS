from app import models, database
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session

# Create tables if they don't exist (just in case)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Get or create a dummy user
user = db.query(models.User).filter(models.User.username == "Curator").first()
if not user:
    print("Creating Curator user...")
    # Try to find any user
    user = db.query(models.User).first()

if not user:
    # Create a user if absolutely no one exists
    user = models.User(
        username="Curator",
        email="curator@museum.com",
        hashed_password="dummy_hash_for_seeding" 
    )
    db.add(user)
    db.commit()
    db.refresh(user)

print(f"Adding artifacts for user: {user.username}")

artifacts_data = [
    {
        "title": "The Starry Night",
        "category": "Art",
        "year": "1889",
        "short_description": "Oil on canvas by Vincent van Gogh.",
        "long_description": "The Starry Night is an oil on canvas by the Dutch post-impressionist painter Vincent van Gogh. Painted in June 1889, it depicts the view from the east-facing window of his asylum room at Saint-Rémy-de-Provence, just before sunrise, with the addition of an idealized village.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
        "likes_count": 150
    },
    {
        "title": "Mona Lisa",
        "category": "Art",
        "year": "1503",
        "short_description": "Portrait by Leonardo da Vinci.",
        "long_description": "The Mona Lisa is a half-length portrait painting by Italian artist Leonardo da Vinci. Considered an archetypal masterpiece of the Italian Renaissance, it has been described as 'the best known, the most visited, the most written about, the most sung about, the most parodied work of art in the world'.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/800px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
        "likes_count": 200
    },
    {
        "title": "The Persistence of Memory",
        "category": "Art",
        "year": "1931",
        "short_description": "Surrealist painting by Salvador Dalí.",
        "long_description": "The Persistence of Memory is a 1931 painting by artist Salvador Dalí and one of the most recognizable works of Surrealism. First shown at the Julien Levy Gallery in 1932, since 1934 the painting has been in the collection of the Museum of Modern Art in New York City, which received it from an anonymous donor.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
        "likes_count": 120
    },
    {
        "title": "Girl with a Pearl Earring",
        "category": "Art",
        "year": "1665",
        "short_description": "Oil painting by Johannes Vermeer.",
        "long_description": "Girl with a Pearl Earring is an oil painting by Dutch Golden Age painter Johannes Vermeer, dated c. 1665. Going by various names over the centuries, it became known by its present title towards the end of the 20th century after the large pearl earring worn by the girl portrayed there.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/1665_Girl_with_a_Pearl_Earring.jpg/800px-1665_Girl_with_a_Pearl_Earring.jpg",
        "likes_count": 180
    },
    {
        "title": "The Great Wave off Kanagawa",
        "category": "Art",
        "year": "1831",
        "short_description": "Woodblock print by Hokusai.",
        "long_description": "The Great Wave off Kanagawa is a woodblock print by the Japanese ukiyo-e artist Hokusai. It was published sometime between 1829 and 1833 in the late Edo period as the first print in Hokusai's series Thirty-six Views of Mount Fuji.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Great_Wave_off_Kanagawa2.jpg/1280px-Great_Wave_off_Kanagawa2.jpg",
        "likes_count": 160
    },
    {
        "title": "The Scream",
        "category": "Art",
        "year": "1893",
        "short_description": "Expressionist painting by Edvard Munch.",
        "long_description": "The Scream is the popular name given to a composition created by Norwegian Expressionist artist Edvard Munch in 1893. The original German title given by Munch to his work was Der Schrei der Natur (The Scream of Nature), and the Norwegian title is Skrik (Shriek).",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg/800px-Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
        "likes_count": 140
    },
    {
        "title": "Ancient Greek Vase",
        "category": "History",
        "year": "500 BC",
        "short_description": "Terracotta amphora from Athens.",
        "long_description": "An ancient Greek terracotta amphora, used for storing wine or oil. Decorated with black-figure pottery techniques depicting scenes from mythology.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Dipylon_amphora_close_front.jpg/800px-Dipylon_amphora_close_front.jpg",
        "likes_count": 45
    },
    {
        "title": "Rosetta Stone",
        "category": "History",
        "year": "196 BC",
        "short_description": "Granodiorite stele with three scripts.",
        "long_description": "The Rosetta Stone is a stele composed of granodiorite inscribed with three versions of a decree issued in Memphis, Egypt, in 196 BC during the Ptolemaic dynasty on behalf of King Ptolemy V Epiphanes.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Rosetta_Stone.JPG/800px-Rosetta_Stone.JPG",
        "likes_count": 300
    },
    {
        "title": "Antikythera Mechanism",
        "category": "Science",
        "year": "150 BC",
        "short_description": "Ancient Greek hand-powered orrery.",
        "long_description": "The Antikythera mechanism is an ancient Greek hand-powered orrery, described as the oldest example of an analogue computer used to predict astronomical positions and eclipses for calendar and astrological purposes decades in advance.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/NAMA_Machine_d%27Anticyth%C3%A8re_1.jpg/800px-NAMA_Machine_d%27Anticyth%C3%A8re_1.jpg",
        "likes_count": 250
    },
    {
        "title": "Wright Flyer",
        "category": "Science",
        "year": "1903",
        "short_description": "First successful heavier-than-air powered aircraft.",
        "long_description": "The Wright Flyer (often retrospectively referred to as Flyer I or 1903 Flyer) was the first successful heavier-than-air powered aircraft. It was designed and built by the Wright brothers.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/First_flight2.jpg/1200px-First_flight2.jpg",
        "likes_count": 180
    },
    {
        "title": "Apollo 11 Command Module",
        "category": "Space",
        "year": "1969",
        "short_description": "The spacecraft that carried astronauts to the Moon.",
        "long_description": "The Command Module Columbia was the living quarters for the three-person crew during most of the first manned lunar landing mission in July 1969.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Apollo_11_Command_module_Columbia.jpg/800px-Apollo_11_Command_module_Columbia.jpg",
        "likes_count": 500
    },
    {
        "title": "First Transistor",
        "category": "Technology",
        "year": "1947",
        "short_description": "Replica of the first point-contact transistor.",
        "long_description": "The first point-contact transistor was built in 1947 at Bell Labs. It revolutionized the field of electronics, and paved the way for smaller and cheaper radios, calculators, and computers.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Replica-of-first-transistor.jpg/800px-Replica-of-first-transistor.jpg",
        "likes_count": 110
    },
    {
        "title": "T-Rex Skeleton (Sue)",
        "category": "Natural History",
        "year": "67 Million Years Ago",
        "short_description": "The largest, most extensive and best preserved T-Rex specimen.",
        "long_description": "Sue is the nickname given to FMNH PR 2081, which is one of the largest, most extensive, and best preserved Tyrannosaurus rex specimens ever found, at the Field Museum of Natural History in Chicago.",
        "media_type": "image",
        "media_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Sue_the_T._Rex_at_the_Field_Museum.jpg/800px-Sue_the_T._Rex_at_the_Field_Museum.jpg",
        "likes_count": 600
    }
]

for artifact_data in artifacts_data:
    # Check if artifact exists
    existing = db.query(models.Artifact).filter(models.Artifact.title == artifact_data["title"]).first()
    if not existing:
        artifact = models.Artifact(**artifact_data, creator_id=user.id)
        db.add(artifact)
        print(f"Added artifact: {artifact.title}")
    else:
        print(f"Updating artifact: {artifact_data['title']}")
        existing.media_url = artifact_data["media_url"]
        existing.long_description = artifact_data["long_description"]
        existing.short_description = artifact_data["short_description"]
        existing.year = artifact_data["year"]
        existing.category = artifact_data["category"]
        existing.likes_count = artifact_data["likes_count"]
        
db.commit()
print("Seeding complete!")
