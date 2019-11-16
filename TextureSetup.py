import maya.cmds as mc

title='Material and Texture Setup'
win=[]
width=600
height=350
channelName = ['basecolor', 'metalness', 'roughness', 'normal', 'opacity', 'displacement']

def close(*args):
	mc.deleteUI('TS_Window')

def ConnectP2d(*args):
	p2dAttrs = ['coverage','translateFrame','rotateFrame','mirrorU','mirrorV','stagger','wrapU','wrapV','repeatUV','offset','rotateUV','noiseUV','vertexUvOne','vertexUvTwo','vertexUvThree','vertexCameraOne','outUV','outUvFilterSize']
	fileAttrs = ['coverage','translateFrame','rotateFrame','mirrorU','mirrorV','stagger','wrapU','wrapV','repeatUV','offset','rotateUV','noiseUV','vertexUvOne','vertexUvTwo','vertexUvThree','vertexCameraOne','uvCoord','uvFilterSize']

	obj = mc.ls(sl=True)
	file = []
	p2d = []

	#Separate selected nodes file from p2d
	for i in obj:
		type = mc.nodeType(i)
		if type == 'file':
			file.append(i)
		if type == 'place2dTexture':
			p2d.append(i)

	#Create new p2d node if no p2d nodes selected
	if len(p2d) == 0:
		p2d.append(mc.shadingNode('place2dTexture', n='p2d_1', au=True))

	#reconnect progress
	for i in range(len(file)):
		#To avoid error that already connected p2d to file node
		if mc.isConnected(str(p2d[0]+'.'+p2dAttrs[0]), str(file[i]+'.'+fileAttrs[0])) == False:
			#connect every attribute
			for attrIndex in range(len(fileAttrs)):
				mc.connectAttr(p2d[0]+'.'+p2dAttrs[attrIndex], file[i]+'.'+fileAttrs[attrIndex], f=True)

#fix colorSpace in file nodes.
def fix(*args):
	#get all suffix name
	suffix=[]
	for i in channelName:
		suffix.append(mc.textField('tf_'+i, q=True, tx=True))
	#get all color space name
	colorSpace=[]
	for i in channelName:
		colorSpace.append(mc.optionMenu('m_'+i, q=True, sl=True))

	#get selected nodes
	slNode = mc.ls(sl=True)
	for node in slNode:
		type = mc.nodeType(node)
		if type == 'file':
			name = mc.getAttr(node+'.fileTextureName')
			for s in suffix:
				if (name.rfind(s)> -1):
					#set 1 'ignoreColorSpaceFileRules'
					mc.setAttr(node+'.ignoreColorSpaceFileRules', 1)
					#get selected color space
					j = mc.optionMenu('m_'+channelName[suffix.index(s)], q=True, v=True)
					#if Selected Color Space is Raw
					if (j == 'Raw'):
						mc.setAttr(node+'.colorSpace', 'Raw', type='string')

					#if Selected Color Space is sRGB
					if (j == 'sRGB'):
						mc.setAttr(node+'.colorSpace', 'sRGB', type='string')

#connect file nodes to aiStandardSurface.
def connect(*args):
	#exec fix func
	fix()

	#main
	suffix=[]
	for i in channelName:
		suffix.append(mc.textField('tf_'+i, q=True, tx=True))

	#get all selected nodes
	slNode = mc.ls(sl=True)
	file=[]
	material=[]
	for node in slNode:
		type = mc.nodeType(node)
		if (type == 'aiStandardSurface'):
			material.append(node)
		if (type == 'file'):
			file.append(node)

	if (len(material) > 0):
		#connect file nodes
		for i in file:
			name = mc.getAttr(i+'.fileTextureName')
			for j in suffix:
				#does j include suffix?
				if (name.rfind(j)> -1):
					channel = channelName[suffix.index(j)]
					#if basecolor
					if (channel == 'basecolor'):
						mc.connectAttr(i+'.outColor', material[0]+'.baseColor', f=True)
					#if metalness
					if (channel == 'metalness'):
						mc.connectAttr(i+'.outColorR', material[0]+'.metalness', f=True)
					#if roughness
					if (channel == 'roughness'):
						mc.connectAttr(i+'.outColorR', material[0]+'.specularRoughness', f=True)
					#if opacity
					if (channel == 'opacity'):
						mc.connectAttr(i+'.outColor', material[0]+'.opacity', f=True)
					#if normal
					#Not only connecting but also create aiNormalMap node.
					if (channel == 'normal'):
						nNode = mc.shadingNode('aiNormalMap', au=True)
						mc.connectAttr(i+'.outColor', nNode+'.input', f=True)
						mc.connectAttr(nNode+'.outValue', material[0]+'.normalCamera', f=True)

					#if displacement
					#Not only connecting but also create displacementShader node.
					if (channel == 'displacement'):
						#get sg node
						sg = mc.listConnections(material[0], t='shadingEngine')
						#create displacement node
						dNode = mc.shadingNode('displacementShader', au=True)
						#
						mc.connectAttr(i+'.outColorR', dNode+'.displacement', f=True)
						mc.connectAttr(dNode+'.displacement', sg[0]+'.displacementShader', f=True)

#main func
def main(*args):
	#init
	#delete window if there is a same name window
	if(mc.window('TS_Window', ex=True)):
	    mc.deleteUI('TS_Window')
	win = mc.window('TS_Window', title=title, widthHeight=(width,height))

	#create layout
	form = mc.formLayout( numberOfDivisions=100 )
	b_fix = mc.button( label='P2D Fix', height=26, command=ConnectP2d )
	b_connect = mc.button( label='Connect', height=26, command=connect )
	b_close = mc.button( label='Close', height=26, command=close )
	mc.formLayout(
		form, edit=True,\
		attachForm=(
			[b_fix, 'left', 5],\
			[b_fix, 'bottom', 5],\
			[b_connect, 'left', 5],\
			[b_connect, 'bottom', 5],\
			[b_close, 'right', 5],\
			[b_close, 'bottom', 5]
		),\
		attachControl=(
			[b_connect, 'left', 5, b_fix],\
			[b_connect, 'right', 5, b_close]
		),\
		attachPosition=(
			[b_fix, 'right', 0, 33],\
			[b_close, 'left', 0, 66]
		)
	)

	#scrollLayout
	mc.columnLayout(w=width)
	mc.columnLayout()
	mc.text(l='Suffix')
	#basecolor
	mc.rowLayout(nc=3)
	mc.text(l='Basecolor: ')
	mc.textField('tf_basecolor', w=100)
	mc.optionMenu('m_basecolor', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')
	#metalness
	mc.rowLayout(nc=3)
	mc.text(l='Metalness: ')
	mc.textField('tf_metalness', w=100)
	mc.optionMenu('m_metalness', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')
	#specular roughness
	mc.rowLayout(nc=3)
	mc.text(l='Roughness: ')
	mc.textField('tf_roughness', w=100)
	mc.optionMenu('m_roughness', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')
	#normal
	mc.rowLayout(nc=3)
	mc.text(l='Normal: ')
	mc.textField('tf_normal', w=100)
	mc.optionMenu('m_normal', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')
	#opacity
	mc.rowLayout(nc=3)
	mc.text(l='Opacity: ')
	mc.textField('tf_opacity', w=100)
	mc.optionMenu('m_opacity', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')
	#displacement
	mc.rowLayout(nc=3)
	mc.text(l='Displacement: ')
	mc.textField('tf_displacement', w=100)
	mc.optionMenu('m_displacement', l='Color Space:')
	mc.menuItem(l='Raw')
	mc.menuItem(l='sRGB')
	mc.setParent('..')


	mc.setParent('..')

	mc.setParent('..')
	#end scrollLayout

	#init textfield
	mc.textField('tf_basecolor', e=True, tx='_BaseColor')
	mc.textField('tf_metalness', e=True, tx='_Metalness')
	mc.textField('tf_roughness', e=True, tx='_Roughness')
	mc.textField('tf_normal', e=True, tx='_Normal')
	mc.textField('tf_opacity', e=True, tx='_Opacity')
	mc.textField('tf_displacement', e=True, tx='_Displacement')
	mc.optionMenu('m_basecolor', e=True, sl=2)

	mc.showWindow(win)

main()
