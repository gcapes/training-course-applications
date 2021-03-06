# Script to process feedback for Research IT courses.
# Instructions:
    # Download the responses to the google forms questionnaire
    # Call the script with three arguments:
        # python responses.csv archive.csv, emailsforgitpromotion.csv
        # Note: archive.csv contains responses which have already been processed
    # Script returns a list of people who don't use version control.
    # Email them to advertise Git course.
import sys
import os
import csv
import shutil
import csvfromtrainingcatalogue

def check_headers(contents,timecol,emailcol,coursecol,vcscol):
    assert contents[0][timecol]=="Timestamp"
    assert contents[0][emailcol]=="University Of Manchester email address"
    assert contents[0][coursecol]=="Which course did you attend?"
    assert contents[0][vcscol]=='Which version control systems do you use?'

def get_start_row(archivefilename):
    if os.path.isfile(archivefilename):
        # Archive file exists
        archivefile=open(archivefilename)
        archivedata=list(csv.reader(archivefile))
        # There is potentially new data to process
        startrow=len(archivedata)
    else:
        # Archive file doesn't exist, so process all data
        startrow=0

    return startrow 

def get_emails(responsedata,vcscol,emailcol,coursecol,startrow,gitattendance,gitemailcol,gitstatuscol,gitpromoarchive):
    needsgit=[]
    statuslist= [x[gitstatuscol] for x in gitattendance]
    emaillist = [x[gitemailcol] for x in gitattendance]
    
    # Identify those who didn't attend the Git course
    for row in responsedata[startrow:]:
        if row[vcscol]=='None' \
            and row[coursecol]!='Version control with Git and GitHub'\
            and '@' in row[emailcol]: # Check email address has been entered
            needsgit.append(row[2])
    if len(needsgit)>0:
        # Remove duplicates
        needsgit=set(needsgit)

        # Remove entries if feedback shows they have started using VC
        # or attended Git course since leaving feedback for non-Git course.
        for row in responsedata[startrow:]:
            course=row[coursecol]
            vcs=row[vcscol]
            email=row[emailcol]
            if (course=='Version control with Git and GitHub'\
                or vcs!='None') and email in needsgit:
                needsgit.remove(email)
        
            # Remove entries where a learner has applied to or attended the Git course
            # Obviously need to export and load the Git course attendance from training catalogue.

            # Person has applied or attended, and not already been removed from
            # list by feedback processing above.
            if email in emaillist and email in needsgit:
                index=emaillist.index(email)
                if statuslist[index] == 'Applied' or 'Attended' or 'Confirmed' or 'Pending':
                    needsgit.remove(email)
            # Remove person if they have already been emailed once about git course. Don't spam.
            for sublist in gitpromoarchive:
                if email in sublist and email in needsgit:
                    needsgit.remove(email)
            
    return needsgit

# Run the following commands if executed as a script. Ignore if imported as module.
if __name__=="__main__":
    # Check for correct number of arguments
    assert len(sys.argv)==6, ("Five arguments required: "
    	"<currentresponses.csv> <response_archive.csv> <emailgitpromo.csv>,<gitcourseattendance.xls>,<emailgitpromo_archive.csv>")
    
    inputfile=sys.argv[1]
    archivefilename=sys.argv[2]
    gitpromofile=sys.argv[3]
    gitattendancefile=sys.argv[4]
    gitpromoarchivefile=sys.argv[5]
    
    csvfile=open(inputfile)
    contents=list(csv.reader(csvfile))
    
    if os.path.isfile(gitpromoarchivefile):
        gitpromoarchive=list(csv.reader(open(gitpromoarchivefile)))
    else:
        gitpromoarchive=[]
        
    # Check column headers of interest haven't changed
    timecol=0
    emailcol=2
    coursecol=8
    vcscol=6
    check_headers(contents,timecol,emailcol,coursecol,vcscol)
    
    # Check for new responses by comparing against archive file
    startrow=get_start_row(archivefilename)
    
    # Get git course attendance data
    gitattendance=csvfromtrainingcatalogue.attendance_list(gitattendancefile)
    gitstatuscol=8
    gitemailcol=6
    
    # Get list of email addresses for Git course promotion
    needsgit=get_emails(contents,vcscol,emailcol,coursecol,startrow,gitattendance,gitemailcol,gitstatuscol,gitpromoarchive)
    
    # Whether or not there are any matches, print output and update files.
    # This enables use of a makefile.
    print('%i people for Git course promotion' % len(needsgit))    
    
    # Save email addresses to file
    emails=csv.writer(open(gitpromofile,'w'))
    emails.writerow(list(needsgit))
    
    # Overwrite archive with current file
    shutil.copyfile(inputfile,archivefilename)
    
    # Append email list to email archive
    if len(needsgit)>0:
        emailarchivefile = csv.writer(open(gitpromoarchivefile,'a'))
        emailarchivefile.writerow(list(needsgit))
