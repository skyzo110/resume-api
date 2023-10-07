from rest_framework.response import Response
from rest_framework.decorators import api_view
import docx2txt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@api_view(['GET'])
def getData(request):
    job_description = docx2txt.process('api\Salem_Kamoun_EN.docx')
    resume = docx2txt.process('api/resources/description.docx')
 
    content = [job_description, resume]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(content)
    mat = cosine_similarity(count_matrix)
    result= str(mat[1][0]*100) + '%'
    output ={"res":result}
    return Response(result)